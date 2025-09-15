import argparse
import os
import sys

# Allow imports from src/ without installing the package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from actions import set_debug_actions

from laser_gates.app import run


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Laser Gates")
    parser.add_argument(
        "--debug-actions",
        action="store_true",
        help="Enable debug output for action creation",
    )
    args = parser.parse_args()

    # Enable debug action logging if requested.
    # Note: environment variable ARCADEACTIONS_DEBUG is applied automatically
    # at import time; this flag only enables additional logging (does not disable).
    if args.debug_actions:
        set_debug_actions(True)

    run()


if __name__ == "__main__":
    main()
