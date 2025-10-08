import operator
from retry import retry
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject, PyStormElement
from TestPages.PageObjects.BaseObjects.Table import TableConst
from TestPages.PageObjects.BaseObjects.Table.GenericTablePagination import GenericTablePagination
from TestPages.PageObjects.BaseObjects.Table.Rows.AuthoriseAccountRestrictionUpdateProcesses import GenericBaseRow
from TestPages.PageObjects.BaseObjects.Table.TableFooter import TableFooter
from TestPages.WebDriver import ExpectedConditions as EC


class TableFilter:
    def __init__(self,
                 columnName: str,
                 cellValue: str,
                 cellValueComparisionType: operator = operator.eq):

        self.columnName = columnName
        self.cellValue = cellValue
        self.cellValueComparisionType = cellValueComparisionType

    def getPrintable(self):
        return f"{self.columnName}({self.cellValueComparisionType.__qualname__}) with {self.cellValue}({self.cellValueComparisionType.__qualname__})"


class GenericTable(BaseTestObject):
    headerSectionLocator = (By.XPATH, ".//thead")
    headerCellLocator = (By.XPATH, ".//th[contains(@class, 'cell')]")
    dataLocator = (By.XPATH, ".//tbody")
    FOOTER_LOCATOR = (By.XPATH, ".//tfoot")
    rowLocator = (By.XPATH, ".//tr")
    rowType = None

    # to accommodate those tables where first row is header
    firstRowIsHeader = False

    # To handle the generic pagination
    PAGINATION_LOCATOR = None

    def _getIndexFromColumn(self, columnName, comparisonOperator: operator = operator.eq):
        matchingColumns = [k for k in self.headers if comparisonOperator(k.lower(), columnName.lower())]
        if matchingColumns:
            return self.headers.index(matchingColumns[0])
        raise UIException(f"Column '{columnName}' not found.")

    def _getRowsMatchingColumnName(self, rows: list[GenericBaseRow], columnName: str, expectedCellValue: str, comparisionOperator: operator):
        """
        Determine column index from column name
        return rows where cellValue matches expected value in the Column
        """
        columnIndex = self._getIndexFromColumn(columnName, comparisionOperator)

        results = []
        dataRow: GenericBaseRow
        for dataRow in rows:
            cellElement: PyStormElement = dataRow.getCell(columnIndex)

            if cellElement and comparisionOperator(cellElement.text, expectedCellValue):
                results.append(dataRow)

        return results

    @retry(exceptions=TimeoutException, tries=3, delay=15)
    def waitForDataToRender(self, waitToRender=True):
        if not waitToRender:
            return

        waitCondition = EC.presence_of_all_elements_located(self.rowLocator, 1)
        WebDriverWait(self.dataHolder, timeout=10).until(waitCondition, "Waiting for table to contain at least single data row.")

    def getFirstRow(self):
        if self.dataRows:
            return self.dataRows[0]
        return None

    def getLastRow(self):
        if self.dataRows:
            return self.dataRows[len(self.dataRows) - 1]
        return None

    @retry(exceptions=(StaleElementReferenceException, UIException), delay=2, tries=5)
    def getNewlyCreatedRows(self, dateOrTimeStamp, rowFieldName: str = "dateCreated", waitToRender=True):
        """
        returns newly created row under assumption row contains DateTime or Date field
        See example in DealReviewDataRow.dateCreated

        args:
        dateTimeStamp - can be either DATE or DATETIME depending on row data
        """
        self.waitForDataToRender(waitToRender)
        foundRows = [k for k in self.dataRows if getattr(k, rowFieldName) >= dateOrTimeStamp]
        if foundRows:
            PrintMessage(f"Found search result with current date-time: '{getattr(foundRows[0], rowFieldName)}'", inStepMessage=True)
            return foundRows
        errMsg = f"""Failed to find result with current date-time: '{dateOrTimeStamp}',
        found other '{[getattr(k, rowFieldName) for k in self.dataRows]}' items not matching criteria."""
        raise UIException(errMsg)

    def getNewlyCreatedRow(self, dateOrTimeStamp, rowFieldName: str = "dateCreated"):
        """
        returns newly created row under assumption row contains DateTime or Date field
        See example in DealReviewDataRow.dateCreated

        args:
        dateTimeStamp - can be either DATE or DATETIME depending on row data
        """
        matchedRows = self.getNewlyCreatedRows(dateOrTimeStamp, rowFieldName)
        if matchedRows:
            return matchedRows[0]
        return None

    def getNewestRow(self, rowFieldName: str = "dateCreated"):
        """
        Returns newest row. Compares all rows in datetime row and returns newest
        """
        return max(self.dataRows, key=lambda x: getattr(x, rowFieldName))

    @retry(exceptions=UIException, delay=2, tries=5)
    def getRowsByColumn(self, columnName: str, cellValue: str, comparisonOperator=operator.eq, **kwargs) -> list:
        """
        Method makes an attempt to find matching rows for provided parameters
        1. Find matching column in column headers
        2. Find row in data with matched value in expected column
        Default comparison is a full match
        Optionally can use operator.contains to perform less strict comparison

        If pagination is available and no matching rows are found, it will try to navigate to the next page
        """
        dataRows = self.dataRows

        if kwargs.get("reverseOrder"):
            # flips the order to find first match checking from the last
            dataRows.reverse()

        foundRows = self._getRowsMatchingColumnName(dataRows, columnName, cellValue, comparisonOperator)

        orderByColumnName = kwargs.get("orderByColumnName")
        usePagination = kwargs.get("usePagination")

        # Use pagination if available
        if not foundRows and usePagination and self.PAGINATION_LOCATOR:
            if self.paginationListbox.navigateToNextPage():
                return self.getRowsByColumn(columnName, cellValue, comparisonOperator, orderByColumnName=orderByColumnName, usePagination=usePagination)

        if orderByColumnName:
            sortByColumnIndex = self._getIndexFromColumn(orderByColumnName, comparisonOperator) if orderByColumnName else None
            if sortByColumnIndex:
                return sorted(foundRows, key=lambda x: x.getCell(sortByColumnIndex))
        return foundRows

    def getRowsByTableRowPropertyName(self, rowPropertyName, textToCompare, fieldTypeName, comparisonOperator=operator.eq, usePagination=False):
        """
        rowPropertyName - relates to field name in row class
        fieldTypeName - either text or value

        If pagination is available and no matching rows are found, it will try to navigate to the next page
        """
        foundRows = []
        for dataRow in self.dataRows:
            fieldObj = getattr(dataRow, rowPropertyName)
            if isinstance(fieldObj, BaseTestObject):
                fieldText = getattr(fieldObj, fieldTypeName)
                if fieldText and comparisonOperator(fieldText, textToCompare):
                    foundRows.append(dataRow)
            elif isinstance(fieldObj, str):
                if fieldObj and comparisonOperator(fieldObj, textToCompare):
                    foundRows.append(dataRow)

        # Use pagination if available
        if not foundRows and usePagination and self.PAGINATION_LOCATOR:
            if self.paginationListbox.navigateToNextPage():
                return self.getRowsByTableRowPropertyName(rowPropertyName, textToCompare, fieldTypeName, comparisonOperator, usePagination=usePagination)

        return foundRows

    def getRowByFieldText(self, rowPropertyName, textToCompare, comparisonOperator=operator.eq, usePagination=False):
        rows = self.getRowsByTableRowPropertyName(rowPropertyName, textToCompare, TableConst.TYPE_TEXT, comparisonOperator, usePagination=usePagination)
        if len(rows) == 0:
            PrintMessage(f"Row with value: '{textToCompare}' in field '{rowPropertyName}' not found.", inStepMessage=True)
            return None
        return rows[0]

    def getRowByFieldValue(self, rowPropertyName, textToCompare, comparisonOperator=operator.eq, usePagination=False):
        rows = self.getRowsByTableRowPropertyName(rowPropertyName, textToCompare, TableConst.TYPE_VALUE, comparisonOperator, usePagination=usePagination)
        if len(rows) == 0:
            PrintMessage(f"Row with value: '{textToCompare}' in field '{rowPropertyName}' not found.", inStepMessage=True)
            return None
        return rows[0]

    def getRowByColumn(self, columnName, cellValue, comparisonOperator=operator.eq, **kwargs):
        rows = self.getRowsByColumn(columnName, cellValue, comparisonOperator, **kwargs)
        if len(rows) == 0:
            PrintMessage(f"Row with value: '{cellValue}' in column '{columnName}' not found.", inStepMessage=True)
            return None
        return rows[0]

    def getRowByFilter(self, tableFilters: list[TableFilter], usePagination=False):
        """
        retrieves row by using filter containing multiple column names and values
        tableFilter: {ColumnName: A, CellValue: B, ColumnNameComparisionOperator: C, ColumnValueComparisionOperator: D}
        """
        rows = self.dataRows
        for tableFilter in tableFilters:
            rows = self._getRowsMatchingColumnName(rows,
                                                   tableFilter.columnName,
                                                   tableFilter.cellValue,
                                                   tableFilter.cellValueComparisionType)

        if rows:
            return rows[0]

        # Use pagination if available
        if usePagination and self.PAGINATION_LOCATOR:
            if self.paginationListbox.navigateToNextPage():
                return self.getRowByFilter(tableFilters, usePagination=usePagination)
        return None

    def getFirstRowIndex(self):
        """
        Method used to exclude header row in dataRows property
        """
        return 1 if self.firstRowIsHeader else 0

    def getPrintable(self):
        toPrint = []
        for row in self.dataRows:
            toPrint.append(row.text)

        import json
        return json.dumps(toPrint, indent=2)

    @property
    def dataHolder(self):
        if self.element is None:
            return None
        return self.element.find_element(*self.dataLocator) if self.dataLocator else self.element

    @retry(exceptions=UIException, delay=2, tries=5)
    def getHeaders(self, cleanHeaders=False) -> list:
        """
        Retrieves the table headers.

        cleanHeaders (bool): If True, returns only the text before any newline character in each header cell.
                            If False, returns the full text of each header cell.
        """
        headerSection = self.element.find_element(*self.headerSectionLocator)
        if headerSection:
            if cleanHeaders:
                return [k.text.split('\n')[0] for k in headerSection.find_elements(*self.headerCellLocator)]
            return [k.text for k in headerSection.find_elements(*self.headerCellLocator)]
        raise UIException(f"Table headers not found with locator: '{self.headerCellLocator}'")

    @property
    def headers(self) -> list:
        return self.getHeaders(cleanHeaders=False)

    @property
    def dataRows(self):
        dataHolder = self.dataHolder
        if dataHolder is None:
            return []

        allRows = dataHolder.find_elements(*self.rowLocator)

        # pylint: disable = not-callable
        return [self.rowType(self.webdriver, self.parentElement, allRows[index]) for index in range(len(allRows)) if index >= self.getFirstRowIndex()]

    @property
    def headerIndices(self):
        """
        Return the header indices as a dictionary where key is the header name and value is its index.
        """
        if not self.headers:
            raise UIException("No headers found.")
        return {header: index for index, header in enumerate(self.headers)}

    @property
    def paginationListbox(self):
        """
        Returns the pagination listbox if it exists, otherwise returns None.
        """
        return GenericTablePagination(self.webdriver, self.element, self.PAGINATION_LOCATOR)

    @property
    def footer(self):
        return TableFooter(self.webdriver, self.element, *self.FOOTER_LOCATOR)
