#!/bin/bash

# Get the main.*.js file name from /home/build/js/
main_js_file=$(ls /home/build/static/js/main.*.js 2>/dev/null)
if [ -z "$main_js_file" ]; then
    echo "No main.*.js file found in /home/build/static/js/"
    exit 1
fi
# Extract the file name without the path
main_js_file_name=$(basename "$main_js_file")
# Rename the file to build.js
mv "$main_js_file" "/home/build/static/js/build.js"
mv "$main_js_file.map" "/home/build/static/js/build.js.map"
mv "$main_js_file.LICENSE.txt" "/home/build/static/js/build.js.LICENSE.txt"
if [ $? -ne 0 ]; then
    echo "Failed to rename $main_js_file to build.js"
    exit 1
fi

#do the same for /home/build/static/css/
main_css_file=$(ls /home/build/static/css/main.*.css 2>/dev/null)
if [ -z "$main_css_file" ]; then
    echo "No main.*.css file found in /home/build/static/css/"
    exit 1
fi
# Extract the file name without the path
main_css_file_name=$(basename "$main_css_file")
# Rename the file to build.css
mv "$main_css_file" "/home/build/static/css/build.css"
mv "$main_css_file.map" "/home/build/static/css/build.css.map"
if [ $? -ne 0 ]; then
    echo "Failed to rename $main_css_file to build.css"
    exit 1
fi

# Find the same file name in /home/build/index.html and rename it to build.js
index_html_file="/home/build/index.html"    
if [ ! -f "$index_html_file" ]; then
    echo "index.html file not found in /home/build/"
    exit 1
fi
# Use sed to replace the file name in index.html
sed -i "s/$main_js_file_name/build.js/g" "$index_html_file"
if [ $? -ne 0 ]; then
    echo "Failed to rename $main_js_file_name to build.js in $index_html_file"
    exit 1
fi
echo "Successfully renamed $main_js_file_name to build.js in $index_html_file"
# Use sed to replace the file name in index.html
sed -i "s/$main_css_file_name/build.css/g" "$index_html_file"
if [ $? -ne 0 ]; then
    echo "Failed to rename $main_css_file_name to build.css in $index_html_file"
    exit 1
fi
echo "Successfully renamed $main_css_file_name to build.css in $index_html_file"
