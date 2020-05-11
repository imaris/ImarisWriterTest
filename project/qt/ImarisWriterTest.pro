########################## General Configuration
### Template is an application named ImarisWriterTest
TEMPLATE = app
TARGET = ImarisWriterTest

include(../../../../bpQmakeCommonOptions.pro)

### ImarisWriterTest needs the qt libraries, stl, exceptions, multithread comp, and of course release and debug configuration
CONFIG += qt console
VERSION = $${IMARISCONVERT_MAJORVERSION}.$${IMARISCONVERT_MINORVERSION}.$${IMARISCONVERT_PATCHVERSION}

INCLUDEPATH += \
        ../.. \
        ../../../../libs

INCLUDEPATH += \
        $$(BP_OUTPUTDIR)/thirdparty \
        $$(BP_OUTPUTDIR)/thirdparty/boost/include

DEPENDPATH += $${INCLUDEPATH}

### libraries
LIBS += -L$$(BP_OUTPUTDIR)/$${CONFIGURATION}
LIBS += \
        $${LIBHDF_LIB} 

LIBS += \
        $${LIBBPIMARISWRITER_FILE}

win32 {
    LIBS += \
            vfw32.lib \
            netapi32.lib \
            rpcrt4.lib \
            comctl32.lib \
            Ws2_32.lib \
            iphlpapi.lib \
            comdlg32.lib \
            winmm.lib \
            Mpr.lib
}

unix {
    PRE_TARGETDEPS += $${LIBS}
    PRE_TARGETDEPS -= -L$$(BP_OUTPUTDIR)/$${CONFIGURATION} \
                      $${LIBHDF_LIB}
}

macx {
    QMAKE_LFLAGS += -bind_at_load
    LIBS += \
            -framework Accelerate \
            -framework CoreServices \
            -framework SystemConfiguration \
            -framework Carbon
}


# Windows special post link commands
win32 {
    bpCreateCopyCmd($${COPYLIB_HDF}, $$(BP_OUTPUTDIR)\\$${CONFIGURATION})
}

# OS X special post link commands
# switch comment of next two lines if you don't like ImarisWriterTest as a bundle
#unused:macx {
macx {
    # Copy resources needed by ImarisWriterTest
    PRIVATERESOURCES.path = Contents/Resources
    PRIVATERESOURCES.files += \
            ../../../imaris/res/Icon_ims.icns \
            ../../../imaris/res/icon_imx.icns
    QMAKE_BUNDLE_DATA += PRIVATERESOURCES

    # Copy the necessary frameworks for a functional ImarisWriterTest
    PRIVATEFRAMEWORKS.path = Contents/Frameworks

    PRIVATEFRAMEWORKS.files += \
            $${LIBHDF_FILE} \

    PRIVATEFRAMEWORKS.files += \
            $${LIBBPIMARISWRITER_FILE}

    QMAKE_BUNDLE_DATA += PRIVATEFRAMEWORKS


    # relocate libraries
    QMAKE_POST_LINK += chmod 755 "$${DESTDIR}/$${TARGET}.app/$${PRIVATEFRAMEWORKS.path}/"*

    # overwrite PkgInfo created by qmake with our own version. File contains APPLBPIM instead of APPL????
    QMAKE_POST_LINK +=  && echo "APPLBPIM" > "$${DESTDIR}/$${TARGET}.app/Contents/PkgInfo"

    RELOCATELIBS += lib$${LIBHDF5}.$${DLLSUFFIX}
    RELOCATELIBS += libbpimariswriter$${PROJECTSUFFIX}$${DEBUGSUFFIX}.$${BPSTATISTICS_MAJORVERSION}.$${BPSTATISTICS_MINORVERSION}.$${DLLSUFFIX}
                    

    for(lib, RELOCATELIBS) {
        QMAKE_POST_LINK += && $$(BP_SRCDIR)/tools/scripts/unix/install_name_tool_newpaths \
                "$${DESTDIR}/$${TARGET}.app/$${PRIVATEFRAMEWORKS.path}/$${lib}" \
                $${RELOCATELIBS} nd2sdk.framework/Versions/1/nd2sdk "@loader_path/"
    }
    QMAKE_POST_LINK += && $$(BP_SRCDIR)/tools/scripts/unix/install_name_tool_newpaths \
            "$${DESTDIR}/$${TARGET}.app/Contents/MacOS/$${TARGET}" \
            $${RELOCATELIBS} "@executable_path/../Frameworks/"

    # strip libraries, and strip target
    CONFIG(release, debug|release) {
        for(lib, RELOCATELIBS) {
            QMAKE_POST_LINK += && strip -x "$${DESTDIR}/$${TARGET}.app/$${PRIVATEFRAMEWORKS.path}/$${lib}"
        }
        QMAKE_POST_LINK += && strip "$${DESTDIR}/$${TARGET}.app/Contents/MacOS/$${TARGET}"
    }

    # This test should come *after* all deployment tools.
    # Probably the best location is at the very end
    QMAKE_POST_LINK += && (otool -L "$${DESTDIR}/$${TARGET}.app/Contents/MacOS/$${TARGET}" | \
            grep -v "\"$${DESTDIR}/$${TARGET}.app/Contents/MacOS/$${TARGET}\\|/System/Library/Frameworks/\\|/usr/lib/\\|@rpath/\\|@executable_path/\\|@loader_path/\"" | grep "[a-zA-Z0-9]">/dev/zero && \
            echo && \
            echo "-------------------------------------------------------------" && \
            echo " Warning: $${TARGET} is linking against *local* libraries." && \
            echo "-------------------------------------------------------------" && \
            echo || true)
}

# copy property info list to macx bundle (necessary for any macx bundle - which file does Imaris open, version number...)
macx:QMAKE_INFO_PLIST = ../../res/Info.plist

#################################################################################################

include(ImarisWriterTest.pri)
PROJECTDIRECTORY=applications/ImarisWriterTest/project/qt
include(../../../../bpQmakeCommonFileCheck.pro)
