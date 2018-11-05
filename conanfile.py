from conans import ConanFile, CMake, tools
import shutil
#from shutil import copyfile
import os

class GtkdocliteConan(ConanFile):
    name = "gtk-doc-lite"
    version = "1.27"
    description = "GTK-Doc is a project which was started to generate API documentation from comments added to C code"
    url = "https://github.com/conanos/gtk-doc-lite"
    homepage = "https://github.com/GNOME/gdk-pixbuf"
    license = "GPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def __replace(self, filepath, replacements):
        ''' Replaces keys in the 'replacements' dict with their values in file '''
        with open(filepath, 'r') as f:
            content = f.read()
        for k, v in replacements.iteritems():
            content = content.replace(k, v)
        with open(filepath, 'w+') as f:
            f.write(content)

    def source(self):
        tarball_name = 'gtk-doc-{version}.tar'.format(version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'https://gstreamer.freedesktop.org/src/mirror/%s'%(archive_name)
        tools.download(url_, archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('gtk-doc-%s' % self.version, self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        pass

    def package(self):
        with tools.chdir(self.source_subfolder):
            shutil.copyfile("gtkdocize.in", "gtkdocize")
            replacements = {'@PACKAGE@': 'gtk-doc',
                            '@VERSION@': self.version,
                            '@prefix@': self.copy._base_dst,  ##!FIXME prefix
                            '@datarootdir@': '${prefix}/share',
                            '@datadir@': '${datarootdir}'}
            self.__replace("gtkdocize", replacements)
        self.copy("gtkdocize", dst="bin", src=self.source_subfolder)
        self.copy("gtk-doc.m4", dst="share/aclocal", src=self.source_subfolder)
        self.copy("gtk-doc.make", dst="share/gtk-doc/data", src=self.source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)