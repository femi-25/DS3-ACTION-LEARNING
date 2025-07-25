def parse_gxe_output(gxe_output: dict, file_name: str) -> dict:
    expectations = gxe_output.get("expectations", [])

    expected_set = set()
    observed_set = set()
    num_expected_features = None
    num_observed_features = None

    for e in expectations:
        if e['expectation_type'] == 'expect_table_column_count_to_equal':
            num_expected_features = e['kwargs'].get('value')
            num_observed_features = e['result'].get('observed_value')
        elif e['expectation_type'] == 'expect_table_columns_to_match_set':
            expected_set = set(e['kwargs'].get('column_set', []))
            observed_set = set(e['result'].get('observed_value', []))

    new_features = sorted(observed_set - expected_set)
    missing_features = sorted(expected_set - observed_set)

    num_new_features = len(new_features)
    num_missing_features = len(missing_features)

    num_samples = 0
    num_affected_samples = 0
    error_types = set()
    feature_error_stats = []

    for e in expectations:
        if not e.get('success', True):
            error_types.add(e['expectation_type'])
            column = e['kwargs'].get('column')
            result = e.get('result', {})
            if column:
                feature_error_stats.append((
                    column,
                    e['expectation_type'],
                    result.get('element_count', 0),
                    result.get('unexpected_count', 0)
                ))

        result = e.get('result', {})
        num_samples = max(num_samples, result.get('element_count', 0))
        num_affected_samples += result.get('unexpected_count', 0)

    column_error_types = [(f, 'missing') for f in missing_features] + [(f, 'new') for f in new_features]
    num_error_types = len(error_types) + (1 if new_features else 0) + (1 if missing_features else 0)

    return {
        "ingestion_metadata": (file_name,),
        "batch_columns_stats": (
            num_expected_features, num_observed_features,
            num_new_features, num_missing_features,
            num_error_types, num_samples, num_affected_samples
        ),
        "column_error_types": column_error_types,
        "feature_error_stats": feature_error_stats
    }