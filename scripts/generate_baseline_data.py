"""Generate the versioned baseline dataset used by pipeline experiments."""

from src.data_generator import DatasetConfig, generate_orders, save_orders


def main() -> None:
    """Generate and save the baseline synthetic order dataset."""

    config = DatasetConfig(
        row_count=10_000,
        random_seed=42,
        reference_time="2026-01-01T00:00:00Z",
    )

    dataframe = generate_orders(config)
    output_path = save_orders(dataframe)

    print(f"Generated rows: {len(dataframe):,}")
    print(f"Output file: {output_path}")
    print(f"Unique orders: {dataframe['order_id'].nunique():,}")
    print(f"Null values: {int(dataframe.isna().sum().sum()):,}")


if __name__ == "__main__":
    main()