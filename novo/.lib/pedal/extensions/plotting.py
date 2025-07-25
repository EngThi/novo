"""
Extensions related to MatPlotLib.

Mock module for Sandbox.

Assertions.
"""
from pedal import Feedback, CompositeFeedbackFunction, is_sandbox_result, Sandbox
from pedal.assertions import ensure_function_call, prevent_function_call
from pedal.core.feedback import FeedbackResponse
from pedal.core.report import MAIN_REPORT
from pedal.sandbox.data import format_contexts
from pedal.types.builtin import BUILTIN_MODULES
from pedal.types.new_types import ModuleType, FunctionType, NoneType
from pedal.cait.find_node import function_is_called
from pedal.cait.cait_api import parse_program, def_use_error
from pedal.sandbox.commands import get_sandbox

PLOT_LABEL = {'plot': 'line plot',
              'hist': 'histogram',
              'scatter': 'scatter plot'}


class plt_rename_err(Feedback):
    title = "Wrong MatPlotLib Import"
    priority = Feedback.CATEGORIES.SYNTAX
    category = Feedback.CATEGORIES.INSTRUCTOR
    justification = "The name 'plt' appeared in the code with a def-use error."
    constant_fields = {'suggestion': 'import matplotlib.pyplot as plt',
                       'actual': 'matplotlib.pyplot',
                       'expected': 'plt'}
    message_template = ("You have imported the "
                        "{expected:name} module, "
                        "but you did not rename it to {actual:name} "
                        "using {suggestion:python_expression}.")

    def condition(self):
        ast = parse_program(report=self.report)
        plts = [n for n in ast.find_all("Name") if n.id == 'plt']
        if plts and any(def_use_error(plt) for plt in plts):
            return True
        return False


class plt_wrong_import(Feedback):
    title = "Missing MatPlotLib Import"
    priority = Feedback.CATEGORIES.SYNTAX
    category = Feedback.CATEGORIES.INSTRUCTOR
    justification = ("A matplotlib name (e.g., 'plot' or 'hist') was used with"
                     " a def-use error.")
    constant_fields = {'suggestion': 'import matplotlib.pyplot as plt'}
    message_template = ("You have attempted to use the MatPlotLib "
                        "function named {expected:name}. However, you "
                        "imported MatPlotLib in a way that does not "
                        "allow you to use the function directly. I "
                        "recommend you use {actual:python_expression} instead, "
                        "after you use {suggestion:python_expression}.")

    def condition(self):
        ast = parse_program(report=self.report)
        matplotlib_names = ['plot', 'hist', 'scatter',
                            'title', 'xlabel', 'ylabel', 'show']
        for name in matplotlib_names:
            for n in ast.find_all("Name"):
                if n.id == name:
                    if def_use_error(n):
                        self.fields['actual'] = name
                        self.fields['expected'] = "plt." + name
                        return True
        return False


@CompositeFeedbackFunction(plt_rename_err, plt_wrong_import)
def prevent_incorrect_plt(**kwargs):
    """ Confirms that matplotlib.pyplot is being imported correctly. """
    return plt_rename_err(**kwargs) or plt_wrong_import(**kwargs)


@CompositeFeedbackFunction(prevent_function_call, ensure_function_call)
def ensure_correct_plot(function_name, report=MAIN_REPORT, **kwargs):
    """ Checks that the given plot type was correctly called. """
    ensure_function_call(function_name, **kwargs)
    as_code = report.format.python_expression
    for name, description in PLOT_LABEL.items():
        if name == function_name:
            continue
        prevent_function_call(name, **kwargs,
                              message=(f"You have called the {as_code(name)} "
                                       f"function, which makes a {description}."))


class ensure_show(Feedback):
    """ Verifies that the `plt.show` function was called. """
    title = "Missing Show Function"
    category = Feedback.CATEGORIES.INSTRUCTOR
    constant_fields = {'missing': 'plt.show'}
    message_template = ("You have not called the {missing:python_expression} "
                        "function, which actually creates the graph.")
    justification = "The show function was not found as a function call."

    def condition(self):
        return not function_is_called("show")


def compare_data(plt_type, correct, given, special_comparison=None):
    """
    Determines whether the given data matches any of the data found in the
    correct data. This handles plots of different types: if a histogram
    was plotted with the expected data for a line plot, it will return True.

    Args:
        plt_type (str): The expected type of this plot
        correct (List of Int or List of List of Int): The expected data.
        given (Dict): The actual plotted data and information
        special_comparison (callable): A special comparison function to use
            between the data. If None, then will use the ``==`` operator.
    Returns:
        bool: Whether the correct data was found in the given plot.
    """
    if special_comparison is None:
        def special_comparison(left, right):
            return left == right

    # Infer arguments
    if plt_type == 'hist':
        correct_xs = None
        correct_ys = correct
    elif not correct:
        correct_xs = []
        correct_ys = []
    elif isinstance(correct[0], (tuple, list)):
        # We were given a list of lists of ints
        correct_xs, correct_ys = correct
    else:
        # Assume it is a singular list
        correct_xs = list(range(len(correct)))
        correct_ys = correct

    if given['type'] == 'hist':
        return special_comparison(correct_ys, given['values'])
    elif plt_type == 'hist':
        return special_comparison(correct_ys, given['y'])
    else:
        return (special_comparison(correct_xs, given['x']) and
                special_comparison(correct_ys, given['y']))


def describe_data(given, with_x=False):
    if given['type'] == 'hist':
        return given['values']
    elif given['type'] == 'line' and not with_x:
        # TODO: Might need to know if we describe the x-axis too..?
        return given['y']
    else:
        return [given['x'], given['y']]


GRAPH_TYPES = {'line': 'line plot',
               'hist': 'histogram',
               'scatter': 'scatter plot'}


def get_diff(expected, actual, format):
    if isinstance(actual, bool):
        return ("\nI expected the data to be:\n" +
                format.python_value(repr(expected)))
    if len(actual) == 1:
        return ("\nI expected the data to be:\n" +
                format.python_value(repr(expected)) +
                "\nBut instead, the data was:\n" +
                format.python_value(repr(actual[0])))
    return ("\nI expected the data to be:\n" +
            format.python_value(repr(expected)) +
            f"\nBut instead, I found {len(actual)} plots, with this data:\n" +
            "\n".join(format.python_value(repr(a)) for a in actual))


class BadGraphFeedback(FeedbackResponse):
    category = Feedback.CATEGORIES.SPECIFICATION
    valence = Feedback.NEGATIVE_VALENCE
    kind = Feedback.KINDS.CONSTRAINT

    def __init__(self, plt_type, expected, actual, context=None, report=MAIN_REPORT, **kwargs):
        fields = kwargs.setdefault('fields', {})
        fields['plt_type'] = plt_type
        fields['expected'] = expected
        fields['actual'] = actual
        fields['diff_message'] = get_diff(expected, actual, report.format)
        fields['context'] = context
        if is_sandbox_result(context):
            context_id = context._actual_context_id
            sandbox = context._actual_sandbox
            actual_context = sandbox.get_context(context_id)
            fields['context_message'] = "\n "+format_contexts([actual_context], report.format)
        else:
            fields['context_message'] = ""
        super().__init__(plt_type, expected, actual, report=report, **kwargs)


class other_plt(BadGraphFeedback):
    title = "Plotting Another Graph"
    message_template = ("You have created a {plt_type}, but it does not "
                        "have the right data. That data appears to have been "
                        "plotted in another graph.{context_message}")


class wrong_plt_data(BadGraphFeedback):
    title = "Plot Data Incorrect"
    message_template = ("You have created a {plt_type}, but it does not have "
                        "the right data.{context_message}{diff_message}")


class wrong_plt_type(BadGraphFeedback):
    title = "Wrong Plot Type"
    message_template = ("You have plotted the right data, but you appear to "
                        "have not plotted it as a {plt_type}.{context_message}")


class no_plt(BadGraphFeedback):
    title = "Missing Plot"
    message_template = "You have not created a {plt_type} with the proper data.{context_message}"


@CompositeFeedbackFunction(other_plt, wrong_plt_data, wrong_plt_type, no_plt)
def assert_plot(plt_type, data, context=None, special_comparison=None, **kwargs):
    """
    Check whether a plot with the given ``plt_type`` and ``data`` exists.
    If the plot was found successfully, returns False.
    Otherwise, returns the feedback that was detected.

    Args:
        plt_type (str): Either 'line', 'hist', or 'scatter'
        data (list): The expected data to check in the plots. Could be a single
            list of numbers, or a pair of two lists (for scatter/line plots).
    """
    report = kwargs.get("report", MAIN_REPORT)
    # Allow instructor to use "plot" instead of "line" as type
    if plt_type == 'plot':
        plt_type = 'line'
    # Check the plots to see if there is a plot with the data
    type_found = False
    data_found = False
    plots = get_sandbox(report=report).modules.plotting.plots
    appropriate_plots = []
    for graph in plots:
        for a_plot in graph['data']:
            data_found_here = compare_data(plt_type, data, a_plot, special_comparison=special_comparison)
            expected_two_lists = isinstance(data, (tuple, list))
            had_x_values = 'x' in a_plot
            if a_plot['type'] == plt_type and data_found_here:
                return False
            if a_plot['type'] == plt_type:
                type_found = True
                appropriate_plots.append(describe_data(a_plot, not expected_two_lists))
                incompatible_plot_amounts = had_x_values and not expected_two_lists
            if data_found_here:
                data_found = data_found_here
    # Figure out what kind of mistake was made.
    plt_type = GRAPH_TYPES.get(plt_type, plt_type)
    if type_found and data_found:
        return other_plt(plt_type, data, data_found)
    elif plt_type == 'line' and type_found and not data_found and incompatible_plot_amounts:
        return wrong_plt_data(plt_type, data, appropriate_plots, context=context)
    elif type_found:
        return wrong_plt_data(plt_type, data, appropriate_plots, context=context)
    elif data_found:
        return wrong_plt_type(plt_type, data, data_found)
    else:
        return no_plt(plt_type, data, data_found)


def get_plots(report=MAIN_REPORT):
    """
    Retrieves any plots made by the user. The general structure is as follows:

    .. code-block::python

        plots = [
        {
            'title': str,
            'xlabel': str,
            'ylabel': str,
            'legend': bool
            'data': {
                'type': str # either 'line' or 'scatter' or 'hist'
                'label': str
                # If 'hist' type
                'values': list[float]
                # If 'scatter' or 'line' type
                'x': list[float],
                'y': list[float]
            }
        }
        # ...
        ]
    """
    return get_sandbox(report=report).modules.plotting.plots


def clear_plots(report=MAIN_REPORT):
    get_sandbox(report=report).modules.plotting._reset_plots()
