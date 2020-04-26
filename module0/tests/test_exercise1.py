from my_python_script import add_two_numbers

# name of function and the name of the file should start with 'test'
def test_exercise_one():
    student_result = add_two_numbers(3., 5.)
    assert student_result == 8.
