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
Requires: python34-requests
Requires: crontabs

%description
A simple, user configurable, python script to update a route 53 record set with your current public IP.

%install
%{__install} -D %{SOURCE0} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -D %{SOURCE1} %{buildroot}%{_sysconfdir}/cron.d/%{name}
%{__install} -D %{SOURCE2} %{buildroot}%{_bindir}/%{name}
%{__install} -D %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -D %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.timer

%clean
rm -rf %{buildroot}

%files
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.timer

%changelog
