from TestPages.PageEnums import DefaultValues, ChartSettings, Metric, Charts, TimeEnum, General, \
    ActivityType, Scale, ChartOptions
from TestHelpers.TestsVerificationMethods.TestsActivityAndTrendChart import RegressionTestActivityAndTrendChart


class RegressionTestActivityAndTrendChartByBasin(RegressionTestActivityAndTrendChart):
    """
    Original implementation - JIRA BeannieAP-7958
    Updates - BeannieAP-7961
    """

    def setUp(self):
        super(RegressionTestActivityAndTrendChartByBasin, self).setUp()

        self.activity_chart = self.dashboard_page.navigate_to_color_by(ChartOptions.basin).activity_chart

    def test_C11852_CheckActivityAndTrendChartDisplay(self):
        # Setup
        chart_menu = self.activity_chart.open_chart_menu()

        # Assert
        self.check_activity_chart(self.activity_chart,
                                  chart_menu,
                                  count_label=ChartSettings.basin_count,
                                  color_by=ChartOptions.basin)