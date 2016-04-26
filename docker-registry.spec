Summary:	Registry server for Docker
Name:		docker-registry
Version:	0.9.1
Release:	0.1
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	https://github.com/docker/docker-registry/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	ec1e5dc5ae9bbea8cecd4d763c84bf74
URL:		https://github.com/docker/docker-registry
Source1:	%{name}.service
Source2:	%{name}.sysconfig
Source3:	%{name}.sysvinit
BuildRequires:	python-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
BuildRequires:	systemd
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires(post):	/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires(postun):	rc-scripts
Requires:	python-M2Crypto
Requires:	python-PyYAML >= 3.11
Requires:	python-SQLAlchemy >= 0.9.4
Requires:	python-backports-lzma
Requires:	python-blinker >= 1.3
Requires:	python-docker-registry-core >= 2.0.2-1
Requires:	python-flask >= 0.10.1
Requires:	python-gevent >= 1.0.1
Requires:	python-gunicorn >= 19.1.1
Requires:	python-importlib
Requires:	python-requests >= 2.3.0
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Registry server for Docker (hosting/delivering of repositories and
images).

%prep
%setup -q

# Remove the golang implementation
# It's not the main one (yet?)
rm -r contrib/golang_impl
find -name "*.py" -print | xargs sed -i '/flask_cors/d'

%build
%py_build

%install
rm -rf $RPM_BUILD_ROOT
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
cp config/config_sample.yml $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.yml
sed -i 's/\/tmp\/registry/\/var\/lib\/docker-registry/g' $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.yml

%clean
rm -rf $RPM_BUILD_ROOT

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

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG.md LICENSE README.md
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.yml
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}/*
%dir %{_sharedstatedir}/%{name}
%{systemdunitdir}/%{name}.service
