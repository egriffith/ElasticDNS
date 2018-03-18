Name: elasticdns
Version: 1.0.0
Release: 1%{?dist}

Summary: Dynamic DNS Using Amazon Route 53
URL: https://github.com/egriffith/ElasticDNS

License: MIT
Source0: %{name}.conf
Source1: %{name}.cron
Source2: %{name}.py
Source3: %{name}.service
Source4: %{name}.timer

BuildArch: noarch
BuildRequires: systemd
Requires: epel-release
Requires: python34-requests
Requires: crontabs

%description
A simple, user configurable, python script to update a route 53 record set with your current public IP.

%prep
#%autosetup

%install
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}

cp -a %{Source0} %{buildroot}%{_sysconfdir}/%{name}/%{Source0}
cp -a %{Source1} %{buildroot}%{_sysconfdir}/cron.d/%{name}
cp -a %{Source2} %{buildroot}%{_bindir}/%{name}
cp -a %{Source3} %{buildroot}%{_unitdir}/%{Source3}
cp -a %{Source4} %{buildroot}%{_unitdir}}/%{Source4}


%clean
rm -rf %{buildroot}

%files
%config(noreplace) %{_sysconfdir}/%{name}/%{SOURCE0}
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%{_bindir}/%{Source2}
%{_unitdir}/%{Source3}
%{_unitdir}/%{Source4}
%{_localstatedir}/log/%{name}

%changelog
