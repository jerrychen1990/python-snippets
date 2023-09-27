echo "build package"
python setup.py sdist bdist_wheel
echo "upload package"
twine upload dist/*
echo "done"