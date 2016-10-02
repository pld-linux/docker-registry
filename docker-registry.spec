Summary:	Docker Registry 2.0
Name:		docker-registry
Version:	2.5.1
Release:	1
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

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS README.md ROADMAP.md
%dir %{_sysconfdir}/docker
%dir %{_sysconfdir}/docker/registry
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/docker/registry/config.yml
%attr(755,root,root) %{_bindir}/digest
%attr(755,root,root) %{_bindir}/registry
%attr(755,root,root) %{_bindir}/registry-api-descriptor-template
