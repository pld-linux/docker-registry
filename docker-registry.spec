Summary:	Docker Registry 2.0
Name:		docker-registry
Version:	2.5.1
Release:	0.1
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	https://github.com/docker/distribution/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	97f16e2b738b1953c5b62a2275f967be
URL:		https://github.com/docker/distribution
Source1:	%{name}.service
Source2:	%{name}.sysconfig
Source3:	%{name}.sysvinit
BuildRequires:	golang >= 1.5
BuildRequires:	rpmbuild(macros) >= 1.714
%if 0
BuildRequires:	systemd-devel
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires(post):	/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires(postun):	rc-scripts
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# go stuff
%define _enable_debug_packages 0
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
%define import_path	github.com/docker/distribution

%description
Registry server for Docker (hosting/delivering of repositories and
images).

%prep
%setup -qc

# go wants specific directory structure
# otherwise version override via ldflags does not work
install -d src/$(dirname %{import_path})
mv distribution-%{version}/{AUTHORS,*.md} .
mv distribution-%{version} src/%{import_path}

%build
export GOPATH=$(pwd)
cd src/%{import_path}

%{__make} binaries \
	VERSION=v%{version} \
	DOCKER_BUILDTAGS="include_oss include_gcs"

v=$(./bin/registry --version)
v=$(echo "$v" | awk '{print $NF}')
test "$v" = "v%{version}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/docker/registry,%{_bindir}}

cd src/%{import_path}
install -p bin/* $RPM_BUILD_ROOT%{_bindir}
cp -p cmd/registry/config-dev.yml $RPM_BUILD_ROOT%{_sysconfdir}/docker/registry/config.yml

%if 0
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT%{py_sitescriptdir}/%{name} \
	$RPM_BUILD_ROOT%{systemdunitdir} \
	$RPM_BUILD_ROOT%{_sharedstatedir}/%{name} \

cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

# Make sure we set proper WorkingDir in the systemd service file
sed -i "s|#WORKDIR#|%{py_sitescriptdir}/%{name}|" $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
# Make sure we set proper working dir in the sysvinit file
sed -i "s|#WORKDIR#|%{py_sitescriptdir}/%{name}|" $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

cp -a docker_registry tests $RPM_BUILD_ROOT%{py_sitescriptdir}/%{name}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
%post
/sbin/chkconfig --add %{name}
%systemd_post %{name}.service

%preun
if [ $1 -eq 0 ] ; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
if [ "$1" -ge "1" ] ; then
	%service %{name} condrestart
fi
%systemd_reload
%endif

%files
%defattr(644,root,root,755)
%doc AUTHORS README.md ROADMAP.md
%dir %{_sysconfdir}/docker
%dir %{_sysconfdir}/docker/registry
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/docker/registry/config.yml
%attr(755,root,root) %{_bindir}/digest
%attr(755,root,root) %{_bindir}/registry
%attr(755,root,root) %{_bindir}/registry-api-descriptor-template

%if 0
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}/*
%dir %{_sharedstatedir}/%{name}
%{systemdunitdir}/%{name}.service
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.yml
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}/*
%dir %{_sharedstatedir}/%{name}
%{systemdunitdir}/%{name}.service
%endif
