from unittest import TestCase, mock

from fuocore.dispatch import Signal
from fuocore.dispatch import receiver


class A(object):
    def f(self, *args, **kwargs):
        print('a.f called')


def f(*args, **kwargs):
    print('f called')


class SignalTest(TestCase):
    def setUp(self):
        self.a1 = A()
        self.a2 = A()

    def tearDown(self):
        pass

    def test_ref(self):
        s = Signal()
        self.assertTrue(s._ref(self.a1.f) == s._ref(self.a1.f))
        self.assertFalse(s._ref(self.a1.f) == s._ref(self.a2.f))

    def test_connect1(self):
        with mock.patch.object(A, 'f', return_value=None) as mock_method_f:
            s = Signal()
            # pay attention
            self.assertTrue(self.a1.f == self.a2.f == mock_method_f)
            s.connect(self.a1.f)
            s.emit(arg1=1, arg2='hello')
            mock_method_f.assert_called_once_with(arg1=1, arg2='hello')

    @mock.patch('test_signal.f', return_value=None)
    def test_connect2(self, mock_func):
        s = Signal()
        s.connect(f)
        s.emit(arg1=1, arg2='hello')
        s.emit(arg1=1, arg2='hello')
        self.assertEqual(mock_func.call_count, 2)

    @mock.patch('test_signal.f', return_value=None)
    def test_disconnect(self, mock_func):
        s = Signal()
        s.connect(f)
        s.disconnect(f)
        s.emit(arg1=1, arg2='hello')
        self.assertEqual(mock_func.call_count, 0)

    @mock.patch.object(Signal, 'connect')
    def test_receiver(self, mock_connect):
        s = Signal()

        @receiver(s)
        def f():
            pass
        self.assertTrue(mock_connect.called)
