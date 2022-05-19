from selenium.webdriver.common.by import By

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject


class AGHeaderCell(object):
    def __init__(self, cell_element):
        self.cell_element = cell_element

    @property
    def col_id(self):
        return self.cell_element.get_attribute('col-id')

    @property
    def name(self):
        return self.cell_element.text


class AGHeaderRow(object):
    def __init__(self, row_element):
        self.row_element = row_element

    def dict_repr(self):
        return {k.col_id: k.name for k in self.cells}

    @property
    def cells(self):
        cell_elements = self.row_element.find_elements(By.CSS_SELECTOR, ".ag-header-cell")

        if not cell_elements:
            cell_elements = self.row_element.find_elements(By.CSS_SELECTOR, ".ag-header-group-cell")
        return [AGHeaderCell(k) for k in cell_elements]


class AGHeader(BaseTestObject):
    def _items(self, reference_name):
        header_group = self.element.find_element(By.CSS_SELECTOR, "div[ref='{0}']".format(reference_name))
        if header_group:
            return [AGHeaderRow(k) for k in header_group.find_elements(By.CLASS_NAME, "ag-header-row")]
        return []

    @property
    def left_headers(self):
        return self._items('ePinnedLeftHeader')

    @property
    def right_headers(self):
        return self._items('ePinnedRightHeader')

    @property
    def main_headers(self):
        return self._items('eHeaderViewport')


class AGDataCell(object):
    def __init__(self, cell_element, all_headers, numeric_to_float=True):
        self._cell_element = cell_element
        self._headers = all_headers
        self._numeric_to_float = numeric_to_float

    @property
    def _group_headers(self):
        """
        Some tables have more than one column header.
        This property returns group headers
        :return:
        """
        return self._headers[:-1]

    @property
    def _column_headers(self):
        """
        Column headers.
        :return:
        """
        return self._headers[-1]

    @property
    def group_id(self):
        """
        Group id if exists, is part of column id
        '1924.Average Lateral Length (ft)' -> group_id = '1924' and column name = 'Average Lateral Length (ft)'
        :return:
        """
        col_id = self._cell_element.get_attribute('col-id')
        data_pair = col_id.split('.')
        if len(data_pair) > 1:
            return data_pair[0]
        return None

    @property
    def column_name(self):
        """
        Derivative from column header
        :return:
        """
        col_id = self._cell_element.get_attribute('col-id')
        headers_dict = self._column_headers.dict_repr()
        return headers_dict[col_id]

    @property
    def field_value(self):
        """
        Try to return numeric value as float with no formatting.
        Otherwise return it as text (as it just might be string value)
        :return:
        """
        cell_text = self._cell_element.text
        if not self._numeric_to_float:
            # for left pinned data we keep it as it is due to i.e. API values (shown as numeric)
            return cell_text

        try:
            return float(cell_text.replace(',', ''))
        except ValueError:
            return cell_text


class AGRow(object):
    def __init__(self, row_element, column_headers, left_pinned_data=False):
        self._row_element = row_element
        self._headers = column_headers
        self._left_pinned_data = left_pinned_data

    def get_field_value(self, cell_element):
        """
        Try to return numeric value as float with no formatting.
        Otherwise return it as text (as it just might be string value)
        :return:
        """
        cell_text = cell_element.text
        if self._left_pinned_data:
            # for left pinned data we keep it as it is due to i.e. API values (shown as numeric)
            return cell_text

        try:
            return float(cell_text.replace(',', ''))
        except ValueError:
            return cell_text

    def fields_header_with_grouped_id(self, cell_elements, headers_dict):
        """
        Processes data from tables with three headers where a group ID is used to tie complex data.

        What happens here:
            1. Get all data off table first. Data is unsorted.
            2. Process data to make consumption easier.
        :param cell_elements:
        :param headers_dict:
        :return:
        """
        items = []
        grouped_by_id = {}
        for element in cell_elements:
            col_id = element.get_attribute('col-id')
            group_id = self.get_group_id(col_id)
            column_name = headers_dict[col_id]

            if group_id not in grouped_by_id:
                grouped_by_id[group_id] = {}

            grouped_by_id[group_id][column_name] = self.get_field_value(element)

        # process data once its scraped off web page
        for key in list(grouped_by_id.keys()):
            subset = grouped_by_id[key]
            subset['key'] = key
            items.append(subset)

        return sorted(items, key=lambda k: k['key'])

    def fields_single_or_double_headers_with_no_group_id(self, cell_elements, headers_dict):
        data_row = {}
        for element in cell_elements:
            col_id = element.get_attribute('col-id')
            column_name = headers_dict[col_id]

            data_row[column_name] = self.get_field_value(element)

        return data_row

    @property
    def _group_headers(self):
        """
        Some tables have more than one column header.
        This property returns group headers
        :return:
        """
        return self._headers[:-1]

    @property
    def _column_headers(self):
        """
        Column headers.
        :return:
        """
        return self._headers[-1]

    @staticmethod
    def get_group_id(col_id):
        """
        Group id if exists, is part of column id
        '1924.Average Lateral Length (ft)' -> group_id = '1924' and column name = 'Average Lateral Length (ft)'
        :return:
        """
        data_pair = col_id.split('.')
        if len(data_pair) > 1:
            return data_pair[0]
        return None

    @property
    def fields(self):
        cell_elements = self._row_element.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")

        header_count = len(self._headers)
        headers_dict = self._column_headers.dict_repr()

        if self._left_pinned_data:
            return self.fields_single_or_double_headers_with_no_group_id(cell_elements, headers_dict)
        if header_count == 3:
            return self.fields_header_with_grouped_id(cell_elements, headers_dict)
        else:
            return self.fields_single_or_double_headers_with_no_group_id(cell_elements, headers_dict)


class AGTable(BaseTestObject):
    def get_data_rows(self, data_holder_locator, headers, left_pinned_data):
        """
        Get data by specified type. IE Bin 5.
        Tables are with 1-3 header rows. This impacts on how returned data is presented.
        :param left_pinned_data: Indicates data we work with. This means: No casting to int, and group ids in headers
        :param headers:
        :param data_holder_locator:
        :return:
        """
        data_holder = self.element.find_element(By.CSS_SELECTOR, data_holder_locator)
        rows = data_holder.find_elements(By.CSS_SELECTOR, "div[role='row']")
        return [AGRow(k, headers, left_pinned_data) for k in rows]

    @property
    def header(self):
        """
        Data header
        :return:
        """
        return AGHeader(self.element, By.CSS_SELECTOR, "div[ref='headerRoot']")

    @property
    def data_rows(self):
        """
        Main part of table (mid section) between left / right pinned
        :return:
        """
        return self.get_data_rows("div[ref='eBodyViewport']", self.header.main_headers, left_pinned_data=False)

    @property
    def data_by_rows(self):
        """
        Left pinned part of table. Contains 'by' values
        :return:
        """
        return self.get_data_rows("div[ref='eLeftViewportWrapper']", self.header.left_headers, left_pinned_data=True)
