from sanic.exceptions import InvalidUsage


def validate_required_params(param_list, *params):
    """
    Ensures that all required keys exist within a dictionary
    :param param_list: dictionary to validate
    :param params: required parameters
    :return: validated dictionary
    """
    for param in list(params):
        if param not in param_list:
            raise InvalidUsage(f'Parameter "{param}" was missing from the request')

        arg = param_list[param]
        if len(arg) == 0:
            raise InvalidUsage(f'Parameter "{param}" had no data associated with it')

    return param_list
