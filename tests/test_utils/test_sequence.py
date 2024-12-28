import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))


from turtwig.futils.sequence import growby, growby_fs


class TestGrowby:

    # Generates a finite sequence when length is specified
    def test_generates_finite_sequence(self):

        def increment(x):
            return x + 1

        result = list(growby(increment, 0, length=5))
        assert result == [0, 1, 2, 3, 4]

    # Handles length as zero, returning an empty sequence
    def test_handles_zero_length(self):

        def increment(x):
            return x + 1

        result = list(growby(increment, 0, length=0))
        assert result == []


class TestGrowbyFs:

    # Applying a list of functions to the initial value generates the expected sequence
    def test_apply_functions_generates_expected_sequence(self):

        init = 1
        fs = [lambda x: x + 1, lambda x: x * 2, lambda x: x - 3]
        result = list(growby_fs(fs, init))

        assert result == [1, 2, 4, 1]

    # The initial value is None
    def test_initial_value_is_none(self):

        init = None
        fs = [lambda x: 1 if x is None else x + 1, lambda x: x * 2]
        result = list(growby_fs(fs, init))

        assert result == [None, 1, 2]
