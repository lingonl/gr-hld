find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_HLD gnuradio-hld)

FIND_PATH(
    GR_HLD_INCLUDE_DIRS
    NAMES gnuradio/hld/api.h
    HINTS $ENV{HLD_DIR}/include
        ${PC_HLD_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_HLD_LIBRARIES
    NAMES gnuradio-hld
    HINTS $ENV{HLD_DIR}/lib
        ${PC_HLD_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-hldTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_HLD DEFAULT_MSG GR_HLD_LIBRARIES GR_HLD_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_HLD_LIBRARIES GR_HLD_INCLUDE_DIRS)
