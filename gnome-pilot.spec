%define pilot_link_version 2:0.12.3-5

### Abstract ###

Name: gnome-pilot
Version: 2.0.17
Release: 9%{?dist}
License: LGPLv2+ and GPLv2+
Group: Applications/Communications
Summary: GNOME pilot programs
URL: http://live.gnome.org/GnomePilot
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Source: http://download.gnome.org/sources/%{name}/2.0/%{name}-%{version}.tar.bz2
ExcludeArch: s390 s390x

### Patches ###

# RH bug #135304 (sort of)
Patch1: gnome-pilot-2.0.17-fix-conduit-dir.patch

# RH bug #512004 / GNOME bug #584894
Patch2: gnome-pilot-2.0.17-fix-missing-icons.patch

# RH bug #552857
Patch3: gnome-pilot-2.0.17-el6-translation-updates.patch

# RH bug #552857
Patch4: gnome-pilot-2.0.17-el6-translation-updates-2.patch

### Dependencies ###

Requires(post): scrollkeeper
Requires(postun): scrollkeeper

Requires(pre): GConf2
Requires(post): GConf2
Requires(postun): GConf2

Requires: pilot-link >= %{pilot_link_version}

### Build Dependencies ###

BuildRequires: GConf2-devel >= 2.0
BuildRequires: ORBit2-devel >= 2.0.0
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bonobo-activation-devel >= 1.0.3
BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: gnome-panel-devel >= 2.0.6
BuildRequires: gob2 >= 2.0.3
BuildRequires: intltool
BuildRequires: libbonobo-devel >= 2.0.0
BuildRequires: libglade2-devel >= 2.0.0
BuildRequires: libgnome-devel >= 2.0.0
BuildRequires: libgnomeui-devel >= 2.0.0
BuildRequires: libtool
BuildRequires: pilot-link-devel >= %{pilot_link_version}

%description
gnome-pilot is a collection of programs and daemon for integrating
GNOME and the PalmPilot<tm> or other PalmOS<tm> devices.

%package devel
Group: Development/Libraries
Summary: GNOME pilot libraries, includes, etc
Requires: %name = %{version}-%{release}
Requires: ORBit2-devel
Requires: libgnomeui-devel
Requires: pilot-link-devel >= %{pilot_link_version}
Requires: pkgconfig

%description devel
gpilotd libraries and includes.

%prep
%setup -q
%patch1 -p1 -b .fix-conduit-dir
%patch2 -p1 -b .fix-missing-icons
%patch3 -p1 -b .el6-translation-updates
%patch4 -p1 -b .el6-translation-updates-2

%build
autoreconf --force --install
intltoolize --force
%configure --disable-static
cp %{_bindir}/libtool .
perl -pi -e 's|hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=\"-L\\\$libdir\"|g;' libtool
export tagname=CC
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
export tagname=CC
%makeinstall LIBTOOL=%{_bindir}/libtool
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

echo "NotShowIn=GNOME;" >> $RPM_BUILD_ROOT%{_datadir}/applications/gpilotd-control-applet.desktop

desktop-file-install --vendor="" 			\
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications	\
        --remove-category=Application 			\
	--add-category=HardwareSettings			\
        $RPM_BUILD_ROOT%{_datadir}/applications/gpilotd-control-applet.desktop

mv $RPM_BUILD_ROOT/%{_datadir}/gnome-pilot/conduits/*.conduit \
   $RPM_BUILD_ROOT/%{_libdir}/gnome-pilot/conduits/

rm -f $RPM_BUILD_ROOT/%{_libdir}/*.{a,la}
rm -f $RPM_BUILD_ROOT/%{_libdir}/gnome-pilot/conduits/*.{a,la}
rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

# Remove this broken menu item (introduced in 2.0.16).
rm -f $RPM_BUILD_ROOT/%{_datadir}/applications/gpilot-applet.desktop

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule				\
	%{_sysconfdir}/gconf/schemas/pilot.schemas		\
	>& /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	gconftool-2 --makefile-uninstall-rule			\
		%{_sysconfdir}/gconf/schemas/pilot.schemas	\
		>& /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	gconftool-2 --makefile-uninstall-rule			\
		%{_sysconfdir}/gconf/schemas/pilot.schemas	\
		>& /dev/null || :
fi

%postun
/sbin/ldconfig
scrollkeeper-update -q

%files -f %{name}.lang
%defattr(-, root, root)
%doc AUTHORS COPYING NEWS README
%{_sysconfdir}/gconf/schemas/*.schemas
%{_bindir}/*
%{_libdir}/*.so.*
%{_libdir}/bonobo/servers/*
%dir %{_libdir}/gnome-pilot
%dir %{_libdir}/gnome-pilot/conduits
%{_libdir}/gnome-pilot/conduits/*
%{_libexecdir}/*
%{_mandir}/man*/*
%{_datadir}/applications/gpilotd-control-applet.desktop
%dir %{_datadir}/gnome-pilot
%dir %{_datadir}/gnome-pilot/conduits
%dir %{_datadir}/gnome-pilot/glade
%{_datadir}/gnome-pilot/devices.xml
%{_datadir}/gnome-pilot/glade/*
%{_datadir}/idl/gnome-pilot.idl
%{_datadir}/mime-info/palm.*
%{_datadir}/pixmaps/*.png
%{_datadir}/gnome/help/gnome-pilot
%{_datadir}/omf/gnome-pilot

%files devel
%defattr(-, root, root)
%doc ChangeLog
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Aug 09 2010 Matthew Barnes <mbarnes@redhat.com> - 2.0.17-9
- Update translations for Red Hat Supported Languages (RH bug #552857).

* Thu Jun 17 2010 Matthew Barnes <mbarnes@redhat.com> - 2.0.17-8
- Update translations for Red Hat Supported Languages (RH bug #552857).

* Thu Jan 14 2010 Matthew Barnes <mbarnes@redhat.com> - 2.0.17-7
- Fix rpmlint warnings.

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.0.17-6.1
- Rebuilt for RHEL 6

* Tue Aug  4 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.17-6
- Don't show gnome-pilot in the menus. It is already available
  from evolution, and this menuitem about 'PalmOS devices' is just
  confusing in the age of the Palm Pre.

* Sun Aug  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.17-5
- Move ChangeLog to -devel to save some space

* Tue Jul 28 2009 Matthew Barnes <mbarnes@redhat.com> - 2.0.17-4
- Add patch for RH bug #512004 (missing icon in applet).

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 08 2009 Matthew Barnes <mbarnes@redhat.com> - 2.0.17-1
- Update to 2.0.17

* Wed Jul 23 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.0.16-3
- fix license tag

* Wed Feb 27 2008 Matthew Barnes <mbarnes@redhat.com> - 2.0.16-2.fc9
- Remove broken "PilotSync" menu item (RH bug #435118).

* Tue Feb 26 2008 Matthew Barnes <mbarnes@redhat.com> - 2.0.16-1.fc9
- Update to 2.0.16
- Remove patch for RH bug #198211 (fixed upstream).

* Sun Feb 17 2008 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-12.fc9
- Rebuild with GCC 4.3

* Fri Nov 23 2007 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-11.fc9
- Rebuild against newer libpisync.so.

* Wed Oct 03 2007 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-10.fc8
- Remove the GConf schemas in preun, not postun (RH bug #246776).

* Wed Sep 26 2007 Matthias Clasen <mclasen@redhat.com> - 2.0.15-9
- Fix the build with new intltool

* Tue Apr 24 2007 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-8.fc7
- One more revision of the patch to close RH bug #198211.

* Mon Apr 23 2007 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-7.fc7
- Revise patch for RH bug #198211 to match upstream's solution.

* Sat Apr 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.0.15-6
- Don't ship static libraries and .la files

* Wed Apr 18 2007 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-5.fc7
- Add patch for RH bug #198211 (unresolved symbols in libraries).
- Add autoconf and automake as build requirements, since we now have to
  run autoreconf before configure.

* Wed Feb  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.0.15-4
- Use desktop-file-install
- Remove invalid category Application, add HardwareSettings
- Other small spec cleanups
 
* Fri Dec 01 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-3.fc7
- Remove patch for GNOME bug #362565 (fixed upstream).

* Mon Nov 27 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-2.fc7
- Rebuild against pilot-link-0.12.

* Fri Nov 24 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.15-1.fc7
- Update to 2.0.15

* Mon Nov  6 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.14-3.fc7
- Look for conduit files under $(libdir) instead of $(datadir).

* Mon Nov  6 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.14-2.fc7
- Add missing BuildRequires intltool.

* Sun Nov  5 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.14-1.fc7
- Update to 2.0.14
- Add patch for Gnome.org bug #362565 (sleep before syncing).
- Remove unused patches.
- Remove patches fixed upstream:
	gnome-pilot-2.0.10-fix_64bit.patch
	gnome-pilot-2.0.12-fix_icon.patch
	gnome-pilot-2.0.12-defines.patch
	gnome-pilot-2.0.12-move-conduits-code.patch
	gnome-pilot-2.0.12-move-conduits-autotools.patch
	gnome-pilot-2.0.12-port-to-pilot-link-0.12.patch
	gb-309077-attach-48373-fix-xml-properties-leak.patch
	gb-309130-attach-48413-backup-conduit-valgrind-fixes.patch
	rh-161799-attach-116013-backup_conduit_update.diff
	rh-161799-attach-116014-conduits_64bit.diff
- Remove BuildRequires autoconf, automake (no longer needed).

* Thu Aug 10 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.13-16
- Forgot to commit the new patches.

* Thu Aug 10 2006 Matthew Barnes <mbarnes@redhat.com> - 2.0.13-15
- Add patches for RH bug #189294.

* Mon Jul 31 2006 Matthew Barnes <mbarnes@redhat.com> 2.0.13-14
- Cleanup spec file, renumber patches.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.0.13-13.1
- rebuild

* Thu Jun  8 2006 Jeremy Katz <katzj@redhat.com> - 2.0.13-13
- and libtool

* Thu Jun 08 2006 Jesse Keating <jkeating@redhat.com> 2.0.13-12
- Add missing BR gettext, autoconf, automake

* Wed Apr 19 2006 Than Ngo <than@redhat.com> 2.0.13-9 
- apply patch to fix crash with pilot-link 0.11.8 #189294
  thanks to Matt Dave

* Wed Mar 29 2006 Than Ngo <than@redhat.com> 2.0.13-8 
- rebuilt against pilot-link-0.11.8

* Sat Mar 11 2006 Bill Nottingham <notting@redhat.com> 2.0.13-7.fc5.4
- fix pilot-link-version vs pilot_link_version macro/dep confusion

* Tue Feb 28 2006 Karsten Hopp <karsten@redhat.de> 2.0.13-7.fc5.3
- Buildrequires: gob2

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.0.13-7.fc5.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.0.13-7.fc5.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Aug 16 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-7.fc5
- rebuild (required by new cairo package)

* Tue Jun 28 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-6.fc5
- Regenerate patch 18 with a fix for a crash in the backup conduit (would crash whenever no modifications had occurred since the last sync)

* Tue Jun 28 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-5.fc5
- Fixed gnome-pilot-2.0.12-move-conduits-autotools.patch to set GNOME_PILOT_CONDUIT_SEARCH_PATH to libdir/gnome-pilot/conduits
  rather than share/gnome-pilot/conduits; should be able to find conduits now.
- Finished removing test conduit

* Mon Jun 27 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-4.fc5
- Introduce pilot-link-version macro; use to bump version to 1:0.12.0-0.pre2.0
- Update gnome-pilot-2.0.12-port-to-pilot-link-0.12.patch to use version by Mark G Adams (#161824; patch 11)
  In addition to the correct port to 0.12, this contains three patches in GNOME bugzilla bug 274032 (error handling, not closing socket on connection, fixed DB reading loop)
- Renabled backup conduit (was patch 12), applying two patches by Mark G Adams (#161799; patch 18 and patch 19)
- Applied patch by Mark G Adams to fix some issues identified using valgrind in the backup conduit (gnome bug 209130, patch 17)
- Applied patch by Mark G Adams to fix some cleanup of XML handling (gnome bug 309077, patch 16)
- Patched to fix a missing #include <pi-error.h> (patch 20)
- Remove test conduit

* Fri Apr 29 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-2
- move .desktop file from /usr/share/control-center-2.0/capplets to 
  /usr/share/applications (#149228)

* Mon Apr 11 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.13-1
- 2.0.13
- removed these patches (now upstream)
  - fix_warnings (#114281)
  - fix_desktop (added in 2.0.12-5)
  - libtool ( linkage of gpilotd)

* Wed Mar 16 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.12-9
- fixed missing $RPM_BUILD_ROOT in move of conduits files; do it in install stanza instead of build
- include the version in build root

* Wed Mar 16 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.12-8
- added various patches I missed to CVS

* Wed Mar 16 2005 David Malcolm <dmalcolm@redhat.com> - 2.0.12-7
- move conduits file from /usr/share/gnome-pilot/conduits to /usr/LIB_DIR/gnome-pilot/conduits (bz #135304)
- initial attempt at porting to pilot-link 0.12 API
- disabled backup conduit for now

* Sun Mar 13 2005 Than Ngo <than@redhat.com> 2.0.12-6
- rebuild against pilot-link-0.12

* Fri Feb 25 2005 Than Ngo <than@redhat.com> 2.0.12-5
- fix broken desktop file

* Fri Oct 15 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.12-4
- use a higher-res icon for the panel applet (bz #135897)

* Tue Sep 21 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.12-3
- added fix for compile-time warnings (bugzilla 114281)

* Mon Sep 20 2004 David Malcolm <dmalcolm@redhat.com>
- rebuilt

* Wed Sep 15 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.12-1
- Update from 2.0.11 to 2.0.12
- Removed patch to fix bx #131560; this is now in the upstream source

* Thu Sep  2 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.11-2
- added patch to fix bz #131560

* Fri Aug 27 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.11-1
- updated from 2.0.10 to 2.0.11
- added the new XML device information file to the package (which replaces a hardcoded array in the code)
- removed patch that added Treo 600 to that array; the Treo 600 is in the XML file
- removed patch for gcc 3.4 support: a version of this is now in the upstream tarball

* Thu Aug 19 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.10-10
- Changed BuildRequires from gnome-panel to gnome-panel-devel (bz #125033)

* Mon Jun 21 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.10-9
- fixes for gcc3.4

* Thu Jun 17 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.10-8
- apply 64-bit build fix (#121268)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt
- use smp_mflags

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Dec  2 2003 Thomas Woerner <twoerner@redhat.com> 2.0.10-5
- removed rpath (patched libtool, removed LIBTOOL=%%{_bindir}/libtool from 
  make call in %%build)

* Fri Nov 28 2003 Jeremy Katz <katzj@redhat.com> 
- call scrollkeeper update in %post (#111159)
- prereq scrollkeeper and GConf2
- -devel should require libgnomeui-devel (#111160)

* Sun Nov  2 2003 Jeremy Katz <katzj@redhat.com> 2.0.10-4
- updated Treo600 patch

* Thu Oct  9 2003 Jeremy Katz <katzj@redhat.com> 2.0.10-3
- add patch from Dax Kelson for Treo600 support (#106731)

* Thu Jul 17 2003 Jeremy Katz <katzj@redhat.com> 2.0.10-1
- 2.0.10

* Tue Jul 15 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-8
- rebuild
- try nuking LIBTOOL=/usr/bin/libtool

* Fri Jun 20 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-6
- rebuild

* Fri Jun 20 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-5
- fix 64bit problems

* Wed Jun 5 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jun  5 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-3
- rebuild

* Mon May 19 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-2
- bye bye test conduit
- remove some unneeded files
- make LIBTOOL=/usr/bin/libtool

* Mon May 19 2003 Jeremy Katz <katzj@redhat.com> 2.0.9-1
- 2.0.9

* Mon May  5 2003 Jeremy Katz <katzj@redhat.com> 2.0.8-1
- 2.0.8

* Mon May  5 2003 Jeremy Katz <katzj@redhat.com> 2.0.7-2
- include the docs

* Mon May  5 2003 Jeremy Katz <katzj@redhat.com> 2.0.7-1
- update to 2.0.7

* Wed Apr 30 2003 Jeremy Katz <katzj@redhat.com> 2.0.6-1
- update to 2.0.6
- drop all patches, unneeded with 2.0 (or will need redoing if not)
- fix file lists
- update build requires to match what's in configure.in

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Dec 12 2002 Jeremy Katz <katzj@redhat.com> 0.1.71-1
- update to 0.1.71, drop obsolete patches

* Fri Dec  6 2002 Jeremy Katz <katzj@redhat.com> 0.1.70-1
- update to 0.1.70, update patches

* Thu Nov  7 2002 Jeremy Katz <katzj@redhat.com> 0.1.69-1
- update to 0.1.69, drop unneeded patches

* Sat Nov  2 2002 Jeremy Katz <katzj@redhat.com> 0.1.67-2
- bump epoch on pilot-link buildrequires

* Sat Nov  2 2002 Jeremy Katz <katzj@redhat.com> 0.1.67-1
- update to 0.1.67

* Fri Oct 18 2002 Jeremy Katz <katzj@redhat.com> 0.1.65-11
- update conduits patch so that new pilots show up in the conduits tab

* Tue Oct  8 2002 Jeremy Katz <katzj@redhat.com> 0.1.65-10
- make default synctype for the pilot apply (#71104)
- add an epoch to the pilot-link requirement (#74575)
- fix applying settings and the try button from the previous patch

* Mon Oct  7 2002 Jeremy Katz <katzj@redhat.com> 0.1.65-9
- put the conduits configuration in the main capplet (#75345)

* Thu Aug 29 2002 Jeremy Katz <katzj@redhat.com> 0.1.65-8
- don't use a relative symlink for the desktop file (#72911)
- include control center desktop files so that capplets work (#71852)

* Thu Aug 22 2002 Than Ngo <than@redhat.com> 0.1.65-7
- rebuild against new pilot-link

* Tue Aug   6 2002 Than Ngo <than@redhat.com> 0.1.65-6
- rebuild against pilot-link-0.11.2

* Mon Jul 29 2002 Jeremy Katz <katzj@redhat.com> 0.1.65-5
- move desktop file to redhat-menus and create symlink here (#69426)

* Thu Jul 18 2002 Than Ngo <than@redhat.com> 0.1.65-4
- rebuild against pilot-link-0.11

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 14 2002 Jeremy Katz <katzj@redhat.com>
- update to 0.1.65

* Mon May 13 2002 Jeremy Katz <katzj@redhat.com>
- rebuild in new environment

* Sun Apr 28 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- do not build on mainframe

* Wed Apr 17 2002 Jeremy Katz <katzj@redhat.com>
- don't build the applet.  now we don't need gnome-core

* Thu Feb 21 2002 Jeremy Katz <katzj@redhat.com>
- go straight through the build system, do not pass go

* Fri Jan 25 2002 Jeremy Katz <katzj@redhat.com>
- rebuild in new environment

* Sun Jan 13 2002 Jeremy Katz <katzj@redhat.com>
- update to 0.1.64

* Mon Nov 26 2001 Jeremy Katz <katzj@redhat.com>
- initial build for Red Hat Linux
- lang'ify
- add build requires

* Tue Sep 11 2001 Eskil Heyn Olsen <eskil@eskil.dk>
- Removed the test conduit from rpm

* Wed Feb 17 1999 Eskil Heyn Olsen <deity@eskil.dk>
- Created the .spec file

