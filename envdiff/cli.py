"""CLI interface for envdiff tool."""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.parser import EnvParser
from envdiff.comparator import EnvComparator
from envdiff.formatter import format_output


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and flag missing or mismatched keys."
    )
    
    parser.add_argument(
        "base",
        type=str,
        help="Base .env file to compare against"
    )
    
    parser.add_argument(
        "targets",
        nargs="+",
        type=str,
        help="Target .env file(s) to compare"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json", "table"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed comparison including values"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    return parser.parse_args(args)


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for CLI."""
    args = parse_args(argv)
    
    # Validate base file exists
    base_path = Path(args.base)
    if not base_path.exists():
        print(f"Error: Base file '{args.base}' not found", file=sys.stderr)
        return 1
    
    # Parse base environment
    parser = EnvParser()
    try:
        base_env = parser.parse_file(str(base_path))
    except Exception as e:
        print(f"Error parsing base file: {e}", file=sys.stderr)
        return 1
    
    # Compare each target
    comparator = EnvComparator(base_env)
    has_any_diff = False
    
    for target in args.targets:
        target_path = Path(target)
        if not target_path.exists():
            print(f"Warning: Target file '{target}' not found, skipping", file=sys.stderr)
            continue
        
        try:
            target_env = parser.parse_file(str(target_path))
            result = comparator.compare(target_env, str(target_path))
            
            output = format_output(
                result,
                format_type=args.format,
                verbose=args.verbose,
                use_color=not args.no_color
            )
            print(output)
            
            if result.has_differences():
                has_any_diff = True
                
        except Exception as e:
            print(f"Error processing '{target}': {e}", file=sys.stderr)
            return 1
    
    return 1 if has_any_diff else 0


if __name__ == "__main__":
    sys.exit(main())
