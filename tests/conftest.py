from __future__ import annotations
import csv
import os
import sys
from pathlib import Path
import shutil
import stat
import tempfile
from typing import Any, Dict, List, TYPE_CHECKING, Optional
import pytest
from tests.fixtures import __test__path__ as test_fixture_path
from tests.fixtures.xml import __test__path__ as xml_fixture_path
from ooodev.utils.lo import Lo as mLo
from ooodev.utils import paths as mPaths
from ooodev.utils.inst.lo.options import Options as LoOptions
from ooodev.conn import connectors

# from ooodev.connect import connectors as mConnectors
from ooodev.conn import cache as mCache

if TYPE_CHECKING:
    from com.sun.star.frame import XComponentLoader
else:
    XComponentLoader = object

# Snap Testing
# Limited Snap testing can be done.
# Mostly it is limited because the snap can't access the real tmp directory.
# To test snap the following must be modified:
# 1. soffice_path()
# 2. soffice_env()
# 3. loader()
# see the comments in each

# os.environ["ODEV_TEST_CONN_SOCKET"] = "true"
# os.environ["ODEV_TEST_HEADLESS"] = "0"
# os.environ[
#     "ODEV_CONN_SOFFICE"
# ] = "D:\\Portables\\PortableApps\\LibreOfficePortable\App\\libreoffice\\program\\soffice.exe"
# NOTE: No success running a portable version on windows from virtual environment.


def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def tmp_path_session():
    result = Path(tempfile.mkdtemp())  # type: ignore
    yield result
    if os.path.exists(result):
        shutil.rmtree(result, onerror=remove_readonly)


@pytest.fixture(scope="session")
def run_headless():
    # windows/powershell
    #   $env:NO_HEADLESS='1'; pytest; Remove-Item Env:\NO_HEADLESS
    # linux
    #  NO_HEADLESS="1" pytest
    return os.environ.get("ODEV_TEST_HEADLESS", "1") == "1"


@pytest.fixture(scope="session")
def fix_printer_name():
    # a printer name that is available on the test system
    # such as "Brother MFC-L2750DW series".
    # Printers such as "Microsoft Print to PDF" will not work for test.
    # see test_calc/test_calc_print.py
    return ""


@pytest.fixture(autouse=True)
def skip_for_headless(request, run_headless: bool):
    # https://stackoverflow.com/questions/28179026/how-to-skip-a-pytest-using-an-external-fixture
    #
    # Also Added:
    # [tool.pytest.ini_options]
    # markers = ["skip_headless: skips a test in headless mode",]
    # see: https://docs.pytest.org/en/stable/how-to/mark.html
    #
    # Usage:
    # @pytest.mark.skip_headless("Requires Dispatch")
    # def test_write(loader, para_text) -> None:
    if run_headless:
        if request.node.get_closest_marker("skip_headless"):
            reason = ""
            try:
                reason = request.node.get_closest_marker("skip_headless").args[0]
            except Exception:
                pass
            if reason:
                pytest.skip(reason)
            else:
                pytest.skip("Skipped in headless mode")


@pytest.fixture(autouse=True)
def skip_not_headless_os(request, run_headless: bool):
    # Usage:
    # @pytest.mark.skip_not_headless_os("linux", "Errors When GUI is present")
    # def test_write(loader, para_text) -> None:

    if not run_headless:
        rq = request.node.get_closest_marker("skip_not_headless_os")
        if rq:
            is_os = sys.platform.startswith(rq.args[0])
            if not is_os:
                return
            reason = ""
            try:
                reason = rq.args[1]
            except Exception:
                pass
            if reason:
                pytest.skip(reason)
            else:
                pytest.skip(f"Skipped in GUI mode on os: {rq.args[0]}")


@pytest.fixture(scope="session")
def soffice_path():
    # allow for a little more development flexibility
    # it is also fine to return "" or None from this function

    # return Path("/snap/bin/libreoffice")

    return mPaths.get_soffice_path()


@pytest.fixture(scope="session")
def soffice_env():
    # for snap testing the PYTHONPATH must be set to the virtual environment
    return {}
    # py_pth = mPaths.get_virtual_env_site_packages_path()
    # py_pth += f":{Path.cwd()}"
    # return {"PYTHONPATH": py_pth}


# region Loader methods
def _get_loader_pipe_default(
    headless: bool, soffice: str, working_dir: Any, env_vars: Optional[Dict[str, str]] = None
) -> XComponentLoader:
    dynamic = os.environ.get("ODEV_TEST_OPT_DYNAMIC", "") == "1"
    verbose = os.environ.get("ODEV_TEST_OPT_VERBOSE", "1") == "1"
    visible = os.environ.get("ODEV_TEST_OPT_VISIBLE", "") == "1"
    return mLo.load_office(
        connector=connectors.ConnectPipe(headless=headless, soffice=soffice, env_vars=env_vars, invisible=not visible),
        cache_obj=mCache.Cache(working_dir=working_dir),
        opt=LoOptions(verbose=verbose, dynamic=dynamic),
    )


def _get_loader_socket_default(
    headless: bool, soffice: str, working_dir: Any, env_vars: Optional[Dict[str, str]] = None
) -> XComponentLoader:
    dynamic = os.environ.get("ODEV_TEST_OPT_DYNAMIC", "") == "1"
    host = os.environ.get("ODEV_TEST_CONN_SOCKET_HOST", "localhost")
    port = int(os.environ.get("ODEV_TEST_CONN_SOCKET_PORT", 2002))
    verbose = os.environ.get("ODEV_TEST_OPT_VERBOSE", "1") == "1"
    visible = os.environ.get("ODEV_TEST_OPT_VISIBLE", "") == "1"
    return mLo.load_office(
        connector=connectors.ConnectSocket(
            host=host, port=port, headless=headless, soffice=soffice, env_vars=env_vars, invisible=not visible
        ),
        cache_obj=mCache.Cache(working_dir=working_dir),
        opt=LoOptions(verbose=verbose, dynamic=dynamic),
    )


def _get_loader_socket_no_start(
    headless: bool, working_dir: Any, env_vars: Optional[Dict[str, str]] = None
) -> XComponentLoader:
    dynamic = os.environ.get("ODEV_TEST_OPT_DYNAMIC", "") == "1"
    host = os.environ.get("ODEV_TEST_CONN_SOCKET_HOST", "localhost")
    port = int(os.environ.get("ODEV_TEST_CONN_SOCKET_PORT", 2002))
    verbose = os.environ.get("ODEV_TEST_OPT_VERBOSE", "1") == "1"
    visible = os.environ.get("ODEV_TEST_OPT_VISIBLE", "") == "1"
    return mLo.load_office(
        connector=connectors.ConnectSocket(
            host=host, port=port, headless=headless, start_office=False, env_vars=env_vars, invisible=not visible
        ),
        cache_obj=mCache.Cache(working_dir=working_dir),
        opt=LoOptions(verbose=verbose, dynamic=dynamic),
    )


@pytest.fixture(scope="session")
def loader(tmp_path_session, run_headless, soffice_path, soffice_env):
    # for testing with a snap the cache_obj must be omitted.
    # This because the snap is not allowed to write to the real tmp directory.
    test_socket = os.environ.get("ODEV_TEST_CONN_SOCKET", "0")
    connect_kind = os.environ.get("ODEV_TEST_CONN_SOCKET_KIND", "default")
    if test_socket == "1":
        if connect_kind == "no_start":
            loader = _get_loader_socket_no_start(
                headless=run_headless, working_dir=tmp_path_session, env_vars=soffice_env
            )
        else:
            loader = _get_loader_socket_default(
                headless=run_headless, soffice=soffice_path, working_dir=tmp_path_session, env_vars=soffice_env
            )
    else:
        loader = _get_loader_pipe_default(
            headless=run_headless, soffice=soffice_path, working_dir=tmp_path_session, env_vars=soffice_env
        )
    yield loader
    if connect_kind == "no_start":
        # only close office if it was started by the test
        return
    mLo.close_office()


# endregion Loader methods


@pytest.fixture(scope="function")
def tmp_path_fn():
    result = Path(tempfile.mkdtemp())
    yield result
    if os.path.exists(result):
        shutil.rmtree(result, onerror=remove_readonly)


@pytest.fixture(scope="session")
def fixture_path():
    return Path(test_fixture_path)


@pytest.fixture(scope="session")
def copy_fix_xml(tmp_path_session):
    def copy_res(fnm):
        src = Path(xml_fixture_path, fnm)
        dst = Path(tmp_path_session, fnm)
        shutil.copy2(src=src, dst=dst)
        return dst

    return copy_res


@pytest.fixture(scope="session")
def fix_xml_path():
    def get_res(fnm: str):
        return Path(xml_fixture_path, fnm)

    return get_res
