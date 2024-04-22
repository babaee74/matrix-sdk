

from .versions import importlib_metadata
from typing import Any, Tuple, Union
import importlib.util
from packaging import version



_sklearn_available = importlib.util.find_spec("sklearn") is not None
if _sklearn_available:
    try:
        importlib_metadata.version("scikit-learn")
    except importlib_metadata.PackageNotFoundError:
        _sklearn_available = False


# doesn't work for all packages, 
def _is_package_available(pkg_name: str, return_version: bool = False) -> Union[Tuple[bool, str], bool]:
    # Check we're not importing a "pkg_name" directory somewhere but the actual library by trying to grab the version
    package_exists = importlib.util.find_spec(pkg_name) is not None
    package_version = "N/A"
    if package_exists:
        try:
            package_version = importlib_metadata.version(pkg_name)
            package_exists = True
        except importlib_metadata.PackageNotFoundError:
            package_exists = False
    if return_version:
        return package_exists, package_version
    else:
        return package_exists

_torch_available, _torch_version = _is_package_available("torch", return_version=True)

_tf_available = importlib.util.find_spec("tensorflow") is not None
if _tf_available:
    candidates = (
        "tensorflow",
        "tensorflow-cpu",
        "tensorflow-gpu",
        "tf-nightly",
        "tf-nightly-cpu",
        "tf-nightly-gpu",
        "intel-tensorflow",
        "intel-tensorflow-avx512",
        "tensorflow-rocm",
        "tensorflow-macos",
        "tensorflow-aarch64",
    )
    _tf_version = None
    # For the metadata, we have to look for both tensorflow and tensorflow-cpu
    for pkg in candidates:
        try:
            _tf_version = importlib_metadata.version(pkg)
            break
        except importlib_metadata.PackageNotFoundError:
            pass
    _tf_available = _tf_version is not None
if _tf_available:
    if version.parse(_tf_version) < version.parse("2"):
        _tf_available = False



def is_tf_available():
    return _tf_available

def is_torch_available():
    return _torch_available

def is_sklearn_available():
    return _sklearn_available
