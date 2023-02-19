import argparse
from pathlib import Path

import numpy as np
import pandas as pd

def inat_data_parser(source, required_fields, deduplicate=True):
    df = pd.read_csv(source, dtype=str)
    # Clean data
    df = df[required_fields]
    if deduplicate:
        df = df.drop_duplicates(['scientific_name'])
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merge iNat (exported) data with local reference data")
    parser.add_argument(dest='inat_data_path', type=Path, 
                        help="Path of the csv file exported from iNat")
    parser.add_argument(dest='ref_data_path', type=Path, 
                        help="Path of the reference csv file")
    parser.add_argument('-o', '--output', dest='output_path', type=Path, default=Path('./output.csv'),
                        help="Path of the output file")
    args = parser.parse_args()

    inat_data = inat_data_parser(args.inat_data_path, required_fields=['scientific_name', 'common_name'])
    inat_data.rename(columns={"common_name": "inat_common_name"}, inplace=True)
    ref_data = pd.read_csv(args.ref_data_path, dtype=str)
    ref_data.rename(columns={ref_data.columns[0]: "scientific_name", ref_data.columns[1]: "ref_common_name"}, inplace=True)
    # Currently based on exported observations (instead of the iNat taxa tree)
    df = inat_data.merge(ref_data, how='left', on='scientific_name')
    df['comment'] = np.where(df.inat_common_name == df.ref_common_name, "Matched", 
                    np.where(df.inat_common_name.isnull(), "Missed common name on iNat", 
                    np.where(df.ref_common_name.isnull(), "Species not included in reference", "Inconsistent common name")))
    df.to_csv(args.output_path, index=False)