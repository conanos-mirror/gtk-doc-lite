from conans import ConanFile, CMake, tools
import shutil
import os
from conanos.build import config_scheme
from conans import Meson

class GtkdocliteConan(ConanFile):
    name = "gtk-doc-lite"
    version = "1.29"
    description = "GTK-Doc is a project which was started to generate API documentation from comments added to C code"
    url = "https://github.com/conanos/gtk-doc-lite"
    homepage = "https://github.com/GNOME/gtk-doc"
    license = "GPLv2Plus"
    patch = 'micro-version-not-exist.patch'
    exports = ["COPYING", patch]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = { 'shared': False, 'fPIC': True }
    _source_subfolder = "source_subfolder"
    _build_subfolder = os.path.join(_source_subfolder,"build")

    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")

        config_scheme(self)
    
    def build_requirements(self):
        self.build_requires("libffi/3.299999@conanos/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        version_='_'.join(self.version.split('.'))
        url_ = 'https://github.com/GNOME/gtk-doc/archive/GTK_DOC_{version}.tar.gz'.format(version=version_)
        tools.get(url_)
        tools.patch(patch_file=self.patch)
        extracted_dir = "gtk-doc-GTK_DOC_" + version_
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["glib","libffi"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        meson = Meson(self)
        defs = {'prefix' : prefix, 'yelp_manual':'false'}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                        pkg_config_paths=pkg_config_paths)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)