
import sys, os, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '{repo_basename}')))


# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', f'{safe_repo_name}')))
# Auto-mock tkinter for headless environments
try:
    import tkinter as tk
except ImportError:
    import sys, types
    class _WidgetMock:
        def __init__(self, *a, **k): self._text = ""
        def config(self, **kwargs): 
            if "text" in kwargs: self._text = kwargs["text"]
        def cget(self, key): return self._text if key == "text" else None
        def get(self): return self._text
        def grid(self, *a, **k): return []
        def pack(self, *a, **k): return []
        def place(self, *a, **k): return []
        def destroy(self): return None
        def __getattr__(self, item): return lambda *a, **k: None
    tk = types.ModuleType("tkinter")
    for widget in ["Tk","Label","Button","Entry","Frame","Canvas","Text","Scrollbar","Checkbutton",
                "Radiobutton","Spinbox","Menu","Toplevel","Listbox"]:
        setattr(tk, widget, _WidgetMock)
    for const in ["N","S","E","W","NE","NW","SE","SW","CENTER","NS","EW","NSEW"]:
        setattr(tk, const, const)
    sys.modules["tkinter"] = tk

import pytest
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, r'/home/vvdn/projects/sfit_unitest_19_9_2025/cloned_repos/Calculator')

from calculator import Calculator, tk, LARGE_FONT_STYLE, SMALL_FONT_STYLE, DIGITS_FONT_STYLE, DEFAULT_FONT_STYLE, OFF_WHITE, WHITE, LIGHT_BLUE, LIGHT_GRAY, LABEL_COLOR

class MockTkinterWidget:
    def __init__(self, *args, **kwargs):
        self.children = {}
        self.config_calls = []
        self.pack_calls = []
        self.grid_calls = []
        self.bind_calls = []

    def configure(self, **kwargs):
        self.config_calls.append(kwargs)

    def pack(self, **kwargs):
        self.pack_calls.append(kwargs)

    def grid(self, **kwargs):
        self.grid_calls.append(kwargs)

    def bind(self, key, func):
        self.bind_calls.append((key, func))

    def config(self, **kwargs):
        self.config_calls.append(kwargs)

    def mainloop(self):
        pass

    def rowconfigure(self, index, weight):
        pass

    def columnconfigure(self, index, weight):
        pass

    def __setitem__(self, key, value):
        self.children[key] = value

    def __getitem__(self, key):
        return self.children[key]

@pytest.fixture
def mock_tkinter():
    mock_tk = MagicMock()
    mock_tk.Tk.return_value = MockTkinterWidget()
    mock_tk.Frame.return_value = MockTkinterWidget()
    mock_tk.Label.return_value = MockTkinterWidget()
    mock_tk.Button.return_value = MockTkinterWidget()
    mock_tk.NSEW = 'nsew'
    return mock_tk

@pytest.fixture
def calculator_instance(mock_tkinter):
    with patch('tkinter.Tk', mock_tkinter.Tk):
        with patch('tkinter.Frame', mock_tkinter.Frame):
            with patch('tkinter.Label', mock_tkinter.Label):
                with patch('tkinter.Button', mock_tkinter.Button):
                    calc = Calculator()
                    yield calc

def test_calculator_initialization(calculator_instance):
    assert calculator_instance.window is not None
    assert calculator_instance.total_expression == ""
    assert calculator_instance.current_expression == ""
    assert calculator_instance.display_frame is not None
    assert calculator_instance.total_label is not None
    assert calculator_instance.label is not None
    assert calculator_instance.buttons_frame is not None

def test_add_to_expression(calculator_instance):
    calculator_instance.label.config = MagicMock()
    calculator_instance.add_to_expression(5)
    assert calculator_instance.current_expression == "5"
    calculator_instance.label.config.assert_called_once_with(text='5')

    calculator_instance.add_to_expression("+")
    assert calculator_instance.current_expression == "5+"
    calculator_instance.label.config.assert_called_with(text='5+')

def test_append_operator(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.label.config = MagicMock()
    calculator_instance.current_expression = "123"
    calculator_instance.append_operator("+")
    assert calculator_instance.total_expression == "123+"
    assert calculator_instance.current_expression == ""
    calculator_instance.total_label.config.assert_called_once_with(text=' 123 + ')
    calculator_instance.label.config.assert_called_once_with(text='')

def test_clear(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.label.config = MagicMock()
    calculator_instance.total_expression = "1+2"
    calculator_instance.current_expression = "3"
    calculator_instance.clear()
    assert calculator_instance.total_expression == ""
    assert calculator_instance.current_expression == ""
    calculator_instance.label.config.assert_called_once_with(text='')
    calculator_instance.total_label.config.assert_called_once_with(text='')

def test_square(calculator_instance):
    calculator_instance.label.config = MagicMock()
    calculator_instance.current_expression = "5"
    calculator_instance.square()
    assert calculator_instance.current_expression == "25"
    calculator_instance.label.config.assert_called_once_with(text='25')

    calculator_instance.current_expression = "-3"
    calculator_instance.square()
    assert calculator_instance.current_expression == "9"
    calculator_instance.label.config.assert_called_with(text='9')

def test_sqrt(calculator_instance):
    calculator_instance.label.config = MagicMock()
    calculator_instance.current_expression = "25"
    calculator_instance.sqrt()
    assert calculator_instance.current_expression == "5.0"
    calculator_instance.label.config.assert_called_once_with(text='5.0')

    calculator_instance.current_expression = "2"
    calculator_instance.sqrt()
    assert calculator_instance.current_expression == "1.4142135623730951"
    calculator_instance.label.config.assert_called_with(text='1.4142135623730951')

def test_evaluate_valid_expression(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.label.config = MagicMock()
    calculator_instance.total_expression = "2+3"
    calculator_instance.current_expression = ""
    calculator_instance.evaluate()
    assert calculator_instance.total_expression == ""
    assert calculator_instance.current_expression == "5"
    calculator_instance.total_label.config.assert_called_once_with(text=' 2 + 3 ')
    calculator_instance.label.config.assert_called_once_with(text='5')

def test_evaluate_expression_with_current(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.label.config = MagicMock()
    calculator_instance.total_expression = "10"
    calculator_instance.current_expression = "*2"
    calculator_instance.evaluate()
    assert calculator_instance.total_expression == ""
    assert calculator_instance.current_expression == "20"
    calculator_instance.total_label.config.assert_called_once_with(text=' 10 * 2 ')
    calculator_instance.label.config.assert_called_once_with(text='20')

def test_evaluate_error_expression(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.label.config = MagicMock()
    calculator_instance.total_expression = "2+"
    calculator_instance.current_expression = ""
    calculator_instance.evaluate()
    assert calculator_instance.total_expression == "2+"
    assert calculator_instance.current_expression == "Error"
    calculator_instance.total_label.config.assert_called_once_with(text=' 2 + ')
    calculator_instance.label.config.assert_called_once_with(text='Error')

def test_update_total_label(calculator_instance):
    calculator_instance.total_label.config = MagicMock()
    calculator_instance.total_expression = "10*5-2"
    calculator_instance.update_total_label()
    calculator_instance.total_label.config.assert_called_with(text='10 × 5 - 2')

def test_update_label(calculator_instance):
    calculator_instance.label.config = MagicMock()
    calculator_instance.current_expression = "1234567890123"
    calculator_instance.update_label()
    calculator_instance.label.config.assert_called_with(text='12345678901')

def test_bind_keys(calculator_instance):
    calculator_instance.evaluate = MagicMock()
    calculator_instance.add_to_expression = Magic