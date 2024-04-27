from typing import Any


def get_sorted_objects(order_results_by: str, analysis_results: list[Any]) -> list[Any]:
    if order_results_by[0] == '-':
        order_reverse = True
        order_results_by = order_results_by[1:]
    else:
        order_reverse = False
    field_none = []
    field_not_none = []
    for net in analysis_results:
        if getattr(net, order_results_by) is None:
            field_none.append(net)
        else:
            field_not_none.append(net)
    field_not_none.sort(key=lambda x: getattr(x, order_results_by), reverse=order_reverse)
    analysis_results = field_not_none + field_none
    if not order_reverse:
        analysis_results = field_not_none + field_none
    else:
        analysis_results = field_none + field_not_none
    return analysis_results