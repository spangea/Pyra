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
from lyra.engine.assumption.assumption_analysis import ForwardDatascienceTypeAnalysis
from lyra.datascience.annotate import annotate
import lyra.config as config

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
        help='warning level to be used (values: potential, plausible)',
        default='potential')
    parser.add_argument(
        '--annotate',
        help='use the results of the ForwardDatascienceTypeAnalysis to annotate the code',
        action='store_true')
    args = parser.parse_args()
    config.args = args

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
    if args.analysis == 'type-datascience':
        # The value of the warning level has to be either 'potential' or 'plausible'
        if args.warning_level not in ['potential', 'plausible']:
            raise ValueError('Warning level must be either potential or plausible')
        result = ForwardDatascienceTypeAnalysis(args.warning_level).main(args.python_file)
        if(args.annotate):
            annotated_code = annotate(result, args.python_file)
    if args.analysis == 'type-vanilla':
        ForwardTypeAnalysis().main(args.python_file)

if __name__ == '__main__':
    main()
