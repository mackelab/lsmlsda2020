from my_python_script import add_integers_up_to_n

# name of function and the name of the file should start with 'test'
def test_exercise_two():
    student_result = add_integers_up_to_n(5.)
    assert student_result == 15.
