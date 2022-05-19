from CommonCode.JsonReader import JsonReader

from TestPages.PageEnums import FiltersOption

body_requests_json_file_path = './Utilities/Libs_API/WMBodyRequests.json'
default_option_settings_json_file_path = './Utilities/Libs_API/APIFilterOptionsConstants.json'


class ChartRequestBody(object):
    benchmark = 'BENCHMARK_CHART_REQUEST_BODY'
    well_metric_correlation = 'WELL_METRIC_CORRELATION_CHART_REQUEST_BODY'
    metric_distribution = 'METRIC_DISTRIBUTION_CHART_REQUEST_BODY'
    pie = 'PIE_CHART_REQUEST_BODY'
    trend_and_activity = 'TREND_AND_ACTIVITY_CHART_REQUEST_BODY'
    historic_production = 'HISTORIC_PRODUCTION_CHART_REQUEST_BODY'
    vintage_profiles = "VINTAGE_PROFILES_CHART_REQUEST_BODY"
    bins_well_count = "BINS_WELL_COUNT_REQUEST_BODY"
    company_ranking = "COMPANY_RANKING_CHART_REQUEST_BODY"


def get_rb_overview(additional_metric_names=None, aggregation_type=None):
    """
    Returns populated overview request body: Additional Metrics
    Same aggregation is applied to all metrics
    :param aggregation_type:
    :param additional_metric_names:
    :return:
    """
    rb_overview = JsonReader(body_requests_json_file_path).load("OVERVIEW_REQUEST_BODY")

    rb_overview.update(get_filters_request_body())

    if not (additional_metric_names and additional_metric_names):
        return rb_overview

    if not isinstance(additional_metric_names, list):
        additional_metric_names = [additional_metric_names]

    for additional_metric_name in additional_metric_names:
        rb_overview["additionalMetrics"].append(dict(aggregationType=aggregation_type, field=additional_metric_name))

    return rb_overview


def get_default_option_settings():
    return JsonReader(default_option_settings_json_file_path).jsonFile


def get_filters_request_body():
    """
    RB: Request Body
    :return:
    """
    request_body = JsonReader(body_requests_json_file_path).load("FILTERS_REQUEST_BODY")
    request_body['filters']['production_date']['name'] = FiltersOption.production_date
    return request_body


def get_rb_chart(chart_name):
    """
    RB: Request Body
    :return:
    """
    return JsonReader(body_requests_json_file_path).load(chart_name)
