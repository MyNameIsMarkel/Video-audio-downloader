cd "$(dirname "$0")" || exit 1

echo "Checking dependencies..."
pip3 install -r requirements.txt

echo
echo "Opening application..."
python3 downloader.py
