"""
Lyra Static Program Analyzer
============================
"""

import argparse
from lyra.engine.liveness.liveness_analysis import StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysisWithSummarization
from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis
from lyra.engine.usage.dataframe_usage_analysis import DataFrameColumnUsageAnalysis

from lyra.engine.numerical.sign_analysis import ForwardSignAnalysis
from lyra.engine.assumption.assumption_analysis import ForwardTypeAnalysis
from lyra.engine.assumption.assumption_analysis import ForwardStatisticalTypeAnalysis


def main():
    """Static analyzer entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'python_file',
        help='Python file to analyze')
    parser.add_argument(
        '--analysis',
        help='analysis to be used (interval, liveness, or usage)',
        default='usage')
    parser.add_argument(
        '--warning-level',
        help='warning level to be used (values: possible, definite)',
        default='possible')

    args = parser.parse_args()

    if args.analysis == 'intervals':
        ForwardIntervalAnalysisWithSummarization().main(args.python_file)
    if args.analysis == 'liveness':
        StrongLivenessAnalysis().main(args.python_file)
    if args.analysis == 'usage':
        SimpleUsageAnalysis().main(args.python_file)
    if args.analysis == 'df_usage':
        DataFrameColumnUsageAnalysis().main(args.python_file)
    if args.analysis == "sign":
        ForwardSignAnalysis().main(args.python_file)
    if args.analysis == 'type-statistical':
        # The value of the warning level has to be either 'possible' or 'definite'
        if args.warning_level not in ['possible', 'definite']:
            raise ValueError('Warning level must be either possible or definite')
        ForwardStatisticalTypeAnalysis(args.warning_level).main(args.python_file)
    if args.analysis == 'type-vanilla':
        ForwardTypeAnalysis().main(args.python_file)

if __name__ == '__main__':
    main()
