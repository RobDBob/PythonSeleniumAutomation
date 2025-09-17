from os import listdir, path
import pandas as pd
from StandAlone.Reports.MonthlyPassRate import ReportConsts


class ProcessPassRateSummary:
    def getReportFilesWithPaths(self, envName):
        reportPaths = []

        for reportFile in listdir(ReportConsts.OUTPUT_FOLDER):
            if envName in reportFile:
                reportPaths.append(path.join(ReportConsts.OUTPUT_FOLDER, reportFile))
        if not reportPaths:
            print(f"no report files were found in '{ReportConsts.OUTPUT_FOLDER}' for environment: '{envName}'")

        return reportPaths

    def runSummary(self, envName):
        reportPaths = self.getReportFilesWithPaths(envName)

        if not reportPaths:
            return 

        df = pd.concat([pd.read_csv(k) for k in reportPaths])

        groupped = df.groupby(ReportConsts.COLUMN_TEST_CASE_OWNER)
        dfTotalCount = groupped.agg(NumberOfTests=pd.NamedAgg(column=ReportConsts.COLUMN_TEST_CASE_OWNER, aggfunc="count"))

        groupped = df.loc[df[ReportConsts.COLUMN_PASS_RATE] == 100].groupby(ReportConsts.COLUMN_TEST_CASE_OWNER)
        df100PassCount = groupped.agg(NumberOfHighs=pd.NamedAgg(column=ReportConsts.COLUMN_TEST_CASE_OWNER, aggfunc="count"))

        dfOut = pd.concat([dfTotalCount, df100PassCount], axis=1)
        dfOut[ReportConsts.COLUMN_PERC] = round(dfOut[ReportConsts.COLUMN_NUMBER_OF_HIGHS] / dfOut[ReportConsts.COLUMN_NUMBER_OF_TESTS] * 100, 2)
        print("\n\r")
        print(f"{envName}:")
        print(dfOut.reset_index().sort_values(by=ReportConsts.COLUMN_PERC, ascending=False).to_string(index=False))


def main():
    processPassRate = ProcessPassRateSummary()
    processPassRate.runSummary("TE5")
    processPassRate.runSummary("UE1")
    processPassRate.runSummary("DE68")


if __name__ == "__main__":
    main()
