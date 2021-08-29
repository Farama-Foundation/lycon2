#!/bin/bash
set -e -u -x


function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}


yum install -y wget
yum install -y zlib-devel
yum install -y libjpeg-devel
yum install -y libpng-devel

for PYBIN in /opt/python/*/bin; do
    if [[ ( "$PYBIN" == *"36"* ) || ( "$PYBIN" == *"37"* ) || ( "$PYBIN" == *"38"* )  || ( "$PYBIN" == *"39"* ) ]]; then
        "${PYBIN}/pip" install -r /io/requirements.txt
        "${PYBIN}/pip" wheel /io/ --no-deps -w wheelhouse/
    fi
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done
