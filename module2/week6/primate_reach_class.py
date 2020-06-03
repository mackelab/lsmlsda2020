# +
import numpy as np
from datetime import datetime

from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt


# -

# Cell
class Primate_Reach(Dataset):
    """Dataset class for Primate reach data

    Combined dataset with neural and behavioral data as well as available group information
    This dataset contains 43 sessions from two monkeys. Trials 0:33 are from 'Indy' and mostly only contain M1 recordings.
    The remaining sessions are from 'Loco' and all have both M1 and S1 data.

    'xa_m' is M1 activity
    'xa_s' is S1 activity
    'xa_j' is all available activity traces (needed ?)
    'xb_y' is finger position (x,y coordinates)
    'xb_d' is finger speed (x,y coordinates)
    'xb_u' is target (x,y coordinates)

    TODO: convert string to Google Docstring style # Auguste
    TODO: Include a function that removes long stretches where the target does not change
    TODO: Maybe add z dimension?

    Parameters
    ----------
    data : list of dicts
        all_sessions.pkl
    session_list : list of ints
        Indicate the sessions that should be processed
    fps : float
        Frequency at which to bin the data
    fr_treshold : float
        Cutoff frequency. Channels with lower firing rate are discarded

    Attributes
    ----------
    behave_rec_hz : float
        Frequency at which behaviour data is recorded
    n_channels : int
        Number of channels of the extracellular recordings
    n_units :
        Number of sorted units per channel
    n_traces : dict
        Number of traces for the different neural / behaviour recordings
    fps : float
        Target fps
    fr_treshold : float
        Minimum firing rate
    session_list : list of ints
        Indicates the session stored
    spike_bs : list of np.array
        Binned spike trains
    spike_mask : list of boolean masks
        Boolean mask that indicates which channels have active neurons
    curser_pos : list of np.array
        Curser position
    finger_pos : list of np.array
        Finger position
    curser_pos : list of np.array
        Curser position (same as Finger position but only x,y)
    session_name : list of str
        Name of the session (contains animal and date)
    session_data : list of datetime
        Dates of the sessions
    animal : list of str
        Indy or Loco
    """

    def __init__(self, data, session_list, fps=100, fr_treshold=0.5):

        self.behave_rec_hz = 250
        self.n_channels = 192
        self.n_units = 5
        self.n_traces = {'xa_j':self.n_channels * self.n_units, 'xa_m': 0.5*self.n_channels * self.n_units, 'xa_s': 0.5*self.n_channels * self.n_units, 'xb_y': 2, 'xb_d': 2, 'xb_u':2}
        self.slices = {'xa_j':np.s_[:], 'xa_m':np.s_[:0.5*self.n_channels * self.n_units], 'xa_s':np.s_[0.5*self.n_channels * self.n_units:]}

        self.fr_treshold = fr_treshold
        self.fps = fps
        self.session_list = session_list

        self.spike_bs = []
        self.spike_mask = []
        self.cursor_pos = []
        self.finger_pos = []
        self.target_pos = []
        self.session_name = []
        self.session_date = []
        self.animal = []
        self.T = []

        for n, session in enumerate([data[i] for i in self.session_list]):

            self.session_name.append(session['session_name'])
            self.session_date.append(datetime(int(self.session_name[-1][5:9]),int(self.session_name[-1][9:11]),int(self.session_name[-1][11:13])))
            self.animal.append(0 if 'indy' in session['session_name'] else 1)

            session_spike_ts = [[] for _ in range(self.n_traces['xa_j'])]

            for c in range(self.n_channels): # channels
                for u in range(self.n_units): # units
                    if len(session['spikes']) > u:
                        if len(session['spikes'][u]) > c:
                            if len(session['spikes'][u][c]) == 1:
                                session_spike_ts[c*self.n_units + u] = session['spikes'][u][c][0]

            session_mask = [len(s) > 0 for s in session_spike_ts]

            tmin = np.min([s[0] for s in [session_spike_ts[b] for b in np.where(session_mask)[0]]])
            tmax = np.max([s[-1] for s in [session_spike_ts[b] for b in np.where(session_mask)[0]]])
            T = tmax-tmin

            tb_min = session['t'][0][0]  # Times where we have behavior data
            tb_max = session['t'][0][-1]

            bin_ts = (np.arange(tmin,tmax,1/self.fps))
            min_ind = np.where(bin_ts > tb_min)[0].min()
            max_ind = np.where(bin_ts < tb_max)[0].max()
            bin_ts = bin_ts[min_ind:max_ind]

            self.T.append(max_ind-min_ind)

            for i in np.where(session_mask)[0]:

                if len(session_spike_ts[i])/T < fr_treshold:
                    session_spike_ts[i] = []
                    session_mask[i] = False

            session_spike_bs = np.zeros([self.n_channels*self.n_units, max_ind-min_ind], dtype=np.uint8)

            for i in np.where(session_mask)[0]:
                session_spike_bs[i] = np.bincount(np.array(((list(session_spike_ts[i])+[tmax])-tmin)*self.fps, dtype='int'))[min_ind:max_ind] # add tmax at the end to ensure all spiketraces have same length

            behave_bins = np.array(np.arange(len(bin_ts))*self.behave_rec_hz/self.fps, dtype=int)

            self.spike_bs.append(session_spike_bs)
            self.spike_mask.append(session_mask)

            self.cursor_pos.append(session['cursor_pos'][:,behave_bins])
            self.finger_pos.append(session['finger_pos'][:,behave_bins])
            self.target_pos.append(session['target_pos'][:,behave_bins])

    def filt_units(self, min_sessions):
        """ Filter out all units that are not active in at least min_sessions sessions """

        self.filt_inds = np.where((np.array(self.spike_mask)*1).sum(0)>=min_sessions)[0]
        for i in range(len(self)):
            self.spike_bs[i] = self.spike_bs[i][self.filt_inds]
            self.spike_mask[i] = list(np.array(self.spike_mask[i])[self.filt_inds])

        self.n_traces['xa_j'] = len(self.filt_inds)
        self.n_traces['xa_m'] = len(np.where(self.filt_inds<self.n_channels/2*self.n_units)[0])
        self.n_traces['xa_s'] = len(np.where(self.filt_inds>=self.n_channels/2*self.n_units)[0])
        self.slices['xa_m'] = np.s_[:self.n_traces['xa_m']]
        self.slices['xa_s'] = np.s_[self.n_traces['xa_m']:]


    def filt_times_ind(self, start=0, end=None):
        """ Filters all time traces by given start and end points """

        for arr in [self.spike_bs, self.cursor_pos, self.finger_pos, self.target_pos]:
            for i in range(len(arr)):
                arr[i] = arr[i][...,start:end]
                self.T[i] = arr[i].shape[-1]

    def filt_times_p(self, percentile=0.8, last=0):
        """ Filters all time traces by a given percentile
        Parameters
        ----------
        percentile : float between 0 and 1
            Percentage of the time that should be kept
        last : bool
            When false return beginning, when true return end of traces
        """

        for arr in [self.spike_bs, self.cursor_pos, self.finger_pos, self.target_pos]:
            for i in range(len(arr)):
                T = int(arr[i].shape[-1] * percentile)
                if last:
                    arr[i] = arr[i][...,T:]
                else:
                    arr[i] = arr[i][...,:T]
                self.T[i] = arr[i].shape[-1]

    def print_act_units(self):
        """ Print the number of active units in each session """
        for i in range(len(self)):
            print(len(np.where(self.spike_bs[i].sum(-1) > 0)[0]))

    def get_train_batch(self, batch_size=20, T=300, to_gpu=False):
        """ Draw a training batch, drawing random session and random starting times
        Parameters
        ----------
        batch_size : int
            Batch size
        T : int
            Length of training sample
        to_gpu : bool
            Whether to load the tensor to the gpu

        Returns
        -------
            batch
                Tensor of size batch_size x T
        """
        batch = {'xa_j':[],'xa_m':[],'xa_s':[],'xb_y':[],'xb_d':[],'xb_u':[],'i':[],'t':[]}
        session = np.random.choice(len(self))
        # session = 1
        for _ in range(batch_size):
            t_min = np.random.choice(self.spike_bs[session].shape[-1]-T, 1)[0]
            batch['xa_m'].append(self.spike_bs[session][:self.n_traces['xa_m'],t_min:t_min+T])
            batch['xa_s'].append(self.spike_bs[session][self.n_traces['xa_m']:self.n_traces['xa_m']+self.n_traces['xa_s'],t_min:t_min+T])
            batch['xa_j'].append(self.spike_bs[session][:,t_min:t_min+T])
            batch['xb_y'].append(self.cursor_pos[session][:,t_min:t_min+T])
            batch['xb_d'].append(padded_diff(self.cursor_pos[session][:,t_min:t_min+T]))
            batch['xb_u'].append(self.target_pos[session][:,t_min:t_min+T])
            batch['t'].append(t_min)
        for k in batch.keys():
            batch[k] = np.array(batch[k])
            if to_gpu: batch[k] = gpu(batch[k])
        batch['i'] = session
        return batch

    def get_session(self, idx, t_slice=np.index_exp[:], outputs=None, to_gpu=False,):
        """ Draw a training batch, drawing random session and random starting times
        Parameters
        ----------
        idx : int
            Indicates session (out of the sessions initially stored)
        t_slice : np.index_ex
            Slice each trace
        outputs : list of str or None
            Indicate which traces to return. If None return all traces.
        to_gpu : bool
            Whether to load the tensor to the gpu
        Returns
        -------
            data
                Dict of traces
        """
        if outputs is None: outputs = self.n_traces.keys()

        if torch.is_tensor(idx):
            idx = idx.tolist()
        data = {}

        if 'xa_j' in outputs: data['xa_j'] = self.spike_bs[idx][None,:,t_slice[0]]
        if 'xa_m' in outputs: data['xa_m'] = self.spike_bs[idx][None,:self.n_traces['xa_m'],t_slice[0]]
        if 'xa_s' in outputs: data['xa_s'] = self.spike_bs[idx][None,self.n_traces['xa_m']:self.n_traces['xa_m']+self.n_traces['xa_s'],t_slice[0]]
        if 'xb_y' in outputs: data['xb_y'] = self.cursor_pos[idx][None,:,t_slice[0]]
        if 'xb_d' in outputs: data['xb_d'] = padded_diff(self.cursor_pos[idx][None,:,t_slice[0]])
        if 'xb_u' in outputs: data['xb_u'] = self.target_pos[idx][None,:,t_slice[0]]

        if to_gpu:
            for k in data.keys():
                data[k] = gpu(data[k])

        data['i'] = idx

        return data

    def plot_behavior(self):
        """ Plot the finger and target position for each session """

        print(self.n_traces)
        plt.figure(figsize=(len(self)*7,4))
        for t in range(len(self)):
            plt.subplot(1,len(self),t+1)
            plt.plot(self.cursor_pos[t][0])
            plt.plot(self.target_pos[t][0])
            plt.title(self.session_name[t])

    def __len__(self):
        """ Return the number of sessions """
        return len(self.session_list)

    def __getitem__(self, idx):
        """ Not in use """
        if torch.is_tensor(idx):
            idx = idx.tolist()

        return None

# Cell
def load_data(model, data, plot=True, train_split=0.7):
    """ Load training and validation data (using the same filtering as for training)
    Args:
        model (model class instance): Trained model
        data (dict): all_sessions.pkl
        plot (bool): Whether to plot behaviour
        train_split (float): between 0 and 1 Train datasplit ratio
    Returns:
        PD_train: train data sets
        PD_valid: test data sets
    """

    PD_train = Primate_Reach(data, model.sessions, fps=model.fps)
    PD_train.filt_units(min_sessions=model.min_shared_sessions)
    if plot:
        PD_train.plot_behavior()
    PD_train.filt_times_p(train_split, last=0)

    PD_valid = Primate_Reach(data, model.sessions, fps=model.fps)
    PD_valid.filt_units(min_sessions=model.min_shared_sessions)
    PD_valid.filt_times_p(train_split, last=1)

    return PD_train, PD_valid


