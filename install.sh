BLENDER_WGET_LINK='https://download.blender.org/release/Blender3.1/blender-3.1.2-linux-x64.tar.xz'
BLENDER_WGET_FILE='blender.tar.xz'
BLENDER_UNTAR_DIR='blender-3.1.2-linux-x64'
BLENDER_PYTHON="blender/3.1/python/bin/python3.10"
BLENDER_INCLUDE="blender/3.1/python/include/python3.10"

PYTHON_WGET_LINK='https://www.python.org/ftp/python/3.10.2/Python-3.10.2.tgz'
PYTHON_WGET_FILE='Python-3.10.2.tgz'
PYTHON_DIR='Python-3.10.2'

if [ ! -d "${BLENDER_DIR}" ]; then
  wget -O "${BLENDER_WGET_FILE}" "${BLENDER_WGET_LINK}"
  tar -xf "${BLENDER_WGET_FILE}"
  mv "${BLENDER_UNTAR_DIR}" "${BLENDER_DIR}"
  rm "${BLENDER_WGET_FILE}"
fi

# Install Conda dependencies
pip install -r requirements.txt

if [ ! -d "${PYTHON_DIR}" ]; then
  # Install Python include file
  wget -O "${PYTHON_WGET_FILE}" "${PYTHON_WGET_LINK}"
  tar -xf "${PYTHON_WGET_FILE}"
  rm "${PYTHON_WGET_FILE}"
fi
cp -r "${PYTHON_DIR}/Include/"* "${BLENDER_INCLUDE}"

# Install Blender dependencies
"${BLENDER_PYTHON}" -m ensurepip
CFLAGS="-I$(realpath ${BLENDER_INCLUDE})" "${BLENDER_PYTHON}" -m pip install -r "${REQUIREMENTS_PATH}"
