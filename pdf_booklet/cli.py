import argparse
import sys
import os
import logging
from pdf_booklet.engine import BookletEngine
from pdf_booklet.exceptions import BookletError
from pdf_booklet.logger import get_logger

logger = get_logger()

def main():
    parser = argparse.ArgumentParser(
        description="pdf-booklet-maker: Convert standard portrait PDFs into booklet format (front/back pages)."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to the input Portrait A4 PDF file (optional if --web is used)."
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save output PDFs. Defaults to the input file's directory."
    )
    parser.add_argument(
        "-g", "--gutter",
        type=float,
        default=0.0,
        help="Base gutter margin in points between left and right pages (default: 0.0)."
    )
    parser.add_argument(
        "-c", "--creep",
        type=float,
        default=0.0,
        help="Creep compensation displacement per sheet in points (default: 0.0)."
    )
    parser.add_argument(
        "--width",
        type=float,
        default=842.0,
        help="Target page width in points (default: 842.0, standard A4 landscape)."
    )
    parser.add_argument(
        "--height",
        type=float,
        default=595.0,
        help="Target page height in points (default: 595.0, standard A4 landscape)."
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the local Web UI server on http://127.0.0.1:8000"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging."
    )

    args = parser.parse_args()

    # Configure verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # If --web is requested, run local web server
    if args.web:
        import uvicorn
        logger.info("Starting Local Web UI via CLI", details={"host": "127.0.0.1", "port": 8000})
        print("==================================================================")
        print(" 📖 pdf-booklet-maker Local Web UI is starting!")
        print(" 👉 Open your browser and navigate to: http://127.0.0.1:8000")
        print(" 💡 Press Ctrl+C in this terminal to stop the server.")
        print("==================================================================")
        
        try:
            from pdf_booklet.web.server import app
            uvicorn.run(app, host="127.0.0.1", port=8000)
        except KeyboardInterrupt:
            logger.info("Local Web UI server stopped by user request.")
        sys.exit(0)

    # If --web is not requested, input_file is required
    if not args.input_file:
        parser.error("the following arguments are required: input_file (or use --web to launch the Web UI)")

    # Resolve input path
    input_path = os.path.abspath(args.input_file)
    
    # Resolve output directory
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.dirname(input_path)

    logger.info("Initializing CLI execution", details={
        "input_file": input_path,
        "output_dir": output_dir,
        "gutter": args.gutter,
        "creep": args.creep
    })

    try:
        engine = BookletEngine(target_width=args.width, target_height=args.height)
        result = engine.make_booklet(
            input_path=input_path,
            output_dir=output_dir,
            base_gutter=args.gutter,
            creep_step=args.creep
        )
        # Success output
        print(f"Booklet generated successfully:")
        print(f"  Front: {result['front_pdf']}")
        print(f"  Back:  {result['back_pdf']}")
        sys.exit(0)
        
    except BookletError as e:
        logger.error("Booklet creation failed due to a validation or processing error", details={
            "error_type": e.__class__.__name__,
            "message": str(e)
        })
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error("Input file not found", details={"message": str(e)})
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected runtime error occurred", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
