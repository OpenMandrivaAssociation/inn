%define _disable_ld_no_undefined 1

%define major	6
%define major_h	3
%define major_s	3
%define libname	%mklibname %{name} %{major}
%define libhist	%mklibname %{name}hist %{major_h}
%define libsto	%mklibname storage %{major_s}
%define devname	%mklibname %{name} -d

Summary:	The InterNetNews (INN) system, a Usenet news server
Name:		inn
Version:	2.6.3
Release:	3
License:	GPLv2+
Group:		System/Servers
URL:		https://www.isc.org/downloads/projects/
Source0:	ftp://ftp.isc.org/isc/inn/inn-%{version}.tar.gz
Source2:	inn-default-distributions
Source10:	http://www.eyrie.org/~eagle/faqs/inn.html
Source11:	inn-tmpfiles.conf
Source20:	innd.service
Source21:	innd-expire.service
Source22:	innd-expire.timer
Source23:	innd-nntpsend.service
Source24:	innd-nntpsend.timer
Source25:	innd-rnews.service
Source26:	innd-rnews.timer
Patch1:		inn-2.6.0-rh.patch
Patch6:		inn-2.5.2.posix.patch
Patch7:		inn-2.4.3.warn.patch
Patch14:	inn-redhat_build.patch
Patch17:	inn-2.5.2-pconf.patch
Patch18:	inn-2.6.1-parallel-buildfix.patch
BuildRequires:	bison
BuildRequires:	perl-ExtUtils-Embed	
BuildRequires:	db-devel
BuildRequires:	flex
BuildRequires:	pkgconfig(openssl) >= 1.1
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(krb5)
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(com_err)
Requires(pre):	chkconfig grep coreutils sed rpm-helper
Requires:	cleanfeed
Requires:	sendmail-command
Requires(post): systemd >= %{systemd_required_version}

%global __requires_exclude perl\\(bigint.pl\\)|perl\\(ftp.pl\\)

%description
INN (InterNetNews) is a complete system for serving Usenet news and/or
private newsfeeds.  INN includes innd, an NNTP (NetNews Transport
Protocol) server, and nnrpd, a newsreader that is spawned for each
client.  Both innd and nnrpd vary slightly from the NNTP protocol, but
not in ways that are easily noticed.

Install the inn package if you need a complete system for serving and
reading Usenet news.  You may also need to install inn-devel, if you
are going to use a separate program which interfaces to INN, like
newsgate or tin.

%package -n	%{libname}
Summary:	Runtime Library needed by %{name}
Group:		System/Libraries

%description -n	%{libname}
Runtime librairy for %{name}.

%package -n	%{libhist}
Summary:	Runtime Library needed by %{name}
Group:		System/Libraries

%description -n	%{libhist}
Runtime librairy for %{name}.

%package -n	%{libsto}
Summary:	Runtime Library needed by %{name}
Group:		System/Libraries

%description -n	%{libsto}
Runtime librairy for %{name}.

%package -n	%{devname}
Summary:	Developements headers for %{name}
Group:		Development/C++
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libhist} = %{version}-%{release}
Requires:	%{libsto} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n	%{devname}
Headers files to build packages against %{name}.

%package -n	inews
Summary:	Sends Usenet articles to a local news server for distribution
Group:		System/Servers
Conflicts:	noffle

%description -n	inews
The inews program is used by some news programs (for example, inn and
trn) to post Usenet news articles to local news servers.  Inews reads
an article from a file or standard input, adds headers, performs some
consistency checks and then sends the article to the local news server
specified in the inn.conf file.

Install inews if you need a program for posting Usenet articles to
local news servers.

%prep
%setup -q
%autopatch -p 1

%build
%serverbuild

%configure \
	--sysconfdir=%{_sysconfdir}/news \
	--bindir=%{_libexecdir}/news \
	--exec-prefix=%{_libexecdir}/news \
	--with-log-dir=/var/log/news --with-spool-dir=/var/spool/news\
	--with-tmp-dir=%{_sharedstatedir}/news/tmp \
	--with-db-dir=/var/lib/news --with-run-dir=/run/news \
	--with-perl --enable-shared --disable-static \
	--enable-tagged-hash \
	--with-libperl-dir=%{perl_vendorlib} \
	--with-news-user=news --with-news-group=news \
	--with-news-master=news \
	--with-openssl \
	--with-sendmail=/usr/sbin/sendmail \
	--with-http-dir=%{_sharedstatedir}/news/http \
	--with-pic

%__make

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_sharedstatedir}/news/http
make install DESTDIR=$RPM_BUILD_ROOT

# -- Install man pages needed by suck et al.
mkdir -p %{buildroot}%{_includedir}/inn
for f in clibrary.h config.h
do
    install -p -m 0644 ./include/$f %{buildroot}%{_includedir}/inn
done
for f in defines.h system.h libinn.h storage.h options.h dbz.h
do
    install -p -m 0644 ./include/inn/$f %{buildroot}%{_includedir}/inn
done

touch %{buildroot}%{_sharedstatedir}/news/history
touch %{buildroot}%{_sharedstatedir}/news/subscriptions
chmod 644 %{buildroot}%{_sharedstatedir}/news/subscriptions

install -m 644 %{SOURCE2} %{buildroot}%{_sharedstatedir}/news/distributions

mkdir -p %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE20} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE21} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE22} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE23} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE24} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE25} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE26} %{buildroot}%{_unitdir}

cp -p %{SOURCE10} FAQ.html

cat > %{buildroot}%{_sysconfdir}/news/.profile <<EOF
PATH=/bin:%{_bindir}:%{_libexecdir}/news
export PATH
EOF

#Fix perms in sample directory to avoid bogus dependencies
find samples -name "*.in" -exec chmod a-x {} \;

# we get this from cleanfeed
rm -f %{buildroot}%{_libexecdir}/news/filter/filter_innd.pl

mkdir -p %{buildroot}%{_bindir}
ln -sf %{_libexecdir}/news/inews %{buildroot}%{_bindir}/inews
ln -sf %{_libexecdir}/news/rnews %{buildroot}%{_bindir}/rnews

# fix debuginfo extraction, permissions are set in files section, anyway
chmod u+w %{buildroot}%{_libdir}/lib{inn{,hist},storage}.so.*
pushd %{buildroot}%{_libexecdir}/news
chmod u+w \
          actsync \
          archive \
          auth/passwd/{auth_krb5,ckpasswd,radius} \
          auth/resolv/{domain,ident} \
          batcher \
          {buff,file,over}chan \
          buffindexed_d \
          convdate \
          ctlinnd \
          cvtbatch \
          expire{,over} \
          fastrm \
          getlist \
          {grep,make,prune}history \
          imapfeed \
          inews \
          inn{bind,confval,d,df,feed,xbatch,xmit} \
          makedbz \
          ninpaths \
          nnrpd \
          nntpget \
          ovdb_{init,monitor,server,stat} \
          rnews{,.libexec/{de,en}code} \
          shlock \
          shrinkfile \
          sm \
          tdx-util \
          tinyleaf
popd

# (sb) doc install conflicts with rpm %%doc, even when config is setup
# correctly. Just rm these files and let %%doc take care of it
rm -fr %{buildroot}/%{_usr}/doc

# Remove unwanted files
rm -rf %{buildroot}%{_libdir}/*.la
rm -rf %{buildroot}%{_libdir}/*.a

install -D -p -m 0644 %{SOURCE11} %{buildroot}%{_tmpfilesdir}/%{name}.conf

# (tv) fix build:
chmod u+rx %{buildroot}/var/lib/news/http

%pre
%_pre_useradd news /etc/news %{_sbindir}/nologin

%pre -n inews
%_pre_useradd news /etc/news %{_sbindir}/nologin

%post
%_tmpfilescreate %{name}
%_post_service innd

umask 002
touch /var/log/news/news.notice
touch /var/log/news/news.crit
touch /var/log/news/news.err
[ -f /var/lib/news/active.times ] || {
    touch /var/lib/news/active.times
    chown news:news /var/lib/news/active.times
}
chown -R news:news /var/log/news*

if [ `hostname -f` ]; then
  if [ `cat /etc/news/inn.conf | grep '^server:' | wc -l` -lt 1 ]; then
    echo "server: `hostname -f`" >> /etc/news/inn.conf
  fi

  if [ -f /var/lib/news/history ]; then
        cd /var/lib/news
	%{_bindir}/makedbz -s `wc -l <history` -f history
        for i in dir hash index pag; do
                [ -f history.n.$i ] && mv history.n.$i history.$i
        done
        chown news:news history.*
        chmod 644 history.*
  else
        cd /var/lib/news
        cp /dev/null history
        %{_bindir}/makehistory 
	%{_bindir}/makedbz -s `wc -l <history` -f history
        for i in dir hash index pag; do
                [ -f history.n.$i ] && mv history.n.$i history.$i
        done
        chown news:news history history.*
        chmod 644 history history.*
  fi
else
  echo "Network misconfigured, manual setup required..."
fi

%preun
%_preun_service innd

if [ $1 = 0 ]; then
    if [ -f /var/lib/news/history.dir ]; then
       rm -f /var/lib/news/history.*
    fi
fi

%postun
if [ "$1" -ge "1" ]; then
    service innd restart > /dev/null 2>&1
fi

%files
%doc NEWS README* HACKING ChangeLog CONTRIBUTORS LICENSE INSTALL FAQ.html
%doc doc/config-design doc/history-innfeed doc/GPL doc/sample-control
%doc doc/config-semantics doc/external-auth TODO doc/hook-python doc/config-syntax
%doc doc/hook-perl doc/history
%doc samples

%defattr(-,root,root)
%{_unitdir}/innd.service
%{_unitdir}/innd-expire.service
%{_unitdir}/innd-expire.timer
%{_unitdir}/innd-nntpsend.service
%{_unitdir}/innd-nntpsend.timer
%{_unitdir}/innd-rnews.service
%{_unitdir}/innd-rnews.timer
%{_tmpfilesdir}/%{name}.conf

%defattr(-,news,news)
%dir %{_sysconfdir}/news
%config(noreplace) %{_sysconfdir}/news/passwd.nntp
%config(noreplace) %{_sysconfdir}/news/send-uucp.cf
%config(noreplace) %{_sysconfdir}/news/actsync.cfg
%config(noreplace) %{_sysconfdir}/news/motd.innd.sample
%config(noreplace) %{_sysconfdir}/news/motd.nnrpd.sample
%config(noreplace) %{_sysconfdir}/news/expire.ctl
%config(noreplace) %{_sysconfdir}/news/actsync.ign
%config(noreplace) %{_sysconfdir}/news/innreport.conf
%config(noreplace) %{_sysconfdir}/news/distrib.pats
%config(noreplace) %{_sysconfdir}/news/buffindexed.conf
%config(noreplace) %{_sysconfdir}/news/innwatch.ctl
%config(noreplace) %{_sysconfdir}/news/nntpsend.ctl
%config(noreplace) %{_sysconfdir}/news/innfeed.conf
%config(noreplace) %{_sysconfdir}/news/nnrpd.track
%config(noreplace) %{_sysconfdir}/news/control.ctl.local
%config(noreplace) %{_sysconfdir}/news/storage.conf
%config(noreplace) %{_sysconfdir}/news/moderators
%config(noreplace) %{_sysconfdir}/news/news2mail.cf
%config(noreplace) %{_sysconfdir}/news/cycbuff.conf
%config(noreplace) %{_sysconfdir}/news/subscriptions
%config(noreplace) %{_sysconfdir}/news/control.ctl
%config(noreplace) %{_sysconfdir}/news/localgroups
%config(noreplace) %{_sysconfdir}/news/.profile
%config(noreplace) %{_sysconfdir}/news/nocem.ctl
%config(noreplace) %{_sysconfdir}/news/incoming.conf
%config(noreplace) %{_sysconfdir}/news/inn-radius.conf
%config(noreplace) %{_sysconfdir}/news/ovdb.conf
%config(noreplace) %{_sysconfdir}/news/newsfeeds
%config(noreplace) %{_sysconfdir}/news/readers.conf
%config(noreplace) %{_sysconfdir}/news/distributions

%dir %{_sharedstatedir}/news
%config(noreplace) %{_sharedstatedir}/news/active
%config(noreplace) %{_sharedstatedir}/news/active.times
%config(noreplace) %{_sharedstatedir}/news/subscriptions
%config(noreplace) %{_sharedstatedir}/news/history
%config(noreplace) %{_sharedstatedir}/news/distributions
%config(noreplace) %{_sharedstatedir}/news/newsgroups

%config(noreplace) %{_sysconfdir}/news/innshellvars.pl.local
%config(noreplace) %{_sysconfdir}/news/innshellvars.local
%config(noreplace) %{_sysconfdir}/news/innshellvars.tcl.local

%defattr(0755,root,news)
%{_bindir}/rnews
%dir %{_libexecdir}/news
%{_libexecdir}/news/controlbatch
%attr(4510,root,news) %{_libexecdir}/news/innbind
%{_libexecdir}/news/docheckgroups
%{_libexecdir}/news/imapfeed
%{_libexecdir}/news/send-nntp
%{_libexecdir}/news/actmerge
%{_libexecdir}/news/ovdb_server
%{_libexecdir}/news/filechan
%{_libexecdir}/news/ninpaths
%{_libexecdir}/news/mod-active
%{_libexecdir}/news/news2mail
%{_libexecdir}/news/innconfval
%{_libexecdir}/news/shlock
%{_libexecdir}/news/nnrpd
%{_libexecdir}/news/controlchan
%{_libexecdir}/news/procbatch
%{_libexecdir}/news/expire
%{_libexecdir}/news/convdate
%{_libexecdir}/news/pullnews
%{_libexecdir}/news/archive
%{_libexecdir}/news/cnfsstat
%{_libexecdir}/news/grephistory
%{_libexecdir}/news/send-ihave
%{_libexecdir}/news/tinyleaf
%{_libexecdir}/news/cvtbatch
%{_libexecdir}/news/expirerm
%{_libexecdir}/news/rc.news
%attr(4550,uucp,news) %{_libexecdir}/news/rnews
%{_libexecdir}/news/innxmit
%{_libexecdir}/news/actsyncd
%{_libexecdir}/news/shrinkfile
%{_libexecdir}/news/makedbz
%{_libexecdir}/news/actsync
%{_libexecdir}/news/pgpverify
%{_libexecdir}/news/inndf
%{_libexecdir}/news/scanlogs
%{_libexecdir}/news/simpleftp
%{_libexecdir}/news/ovdb_init
%{_libexecdir}/news/ctlinnd
%{_libexecdir}/news/innstat
%{_libexecdir}/news/send-uucp
%{_libexecdir}/news/buffchan
%{_libexecdir}/news/perl-nocem
%{_libexecdir}/news/scanspool
%{_libexecdir}/news/expireover
%{_libexecdir}/news/batcher
%{_libexecdir}/news/fastrm
%{_libexecdir}/news/innmail
%{_libexecdir}/news/innxbatch
%{_libexecdir}/news/buffindexed_d
%{_libexecdir}/news/nntpget
%{_libexecdir}/news/cnfsheadconf
%{_libexecdir}/news/ovdb_stat
%{_libexecdir}/news/prunehistory
%{_libexecdir}/news/innreport
%attr(0644,root,news) %{_libexecdir}/news/innreport_inn.pm
%{_libexecdir}/news/getlist
%{_libexecdir}/news/innd
%{_libexecdir}/news/innupgrade
%{_libexecdir}/news/news.daily
%{_libexecdir}/news/sm
%{_libexecdir}/news/innwatch
%{_libexecdir}/news/inncheck
%{_libexecdir}/news/writelog
%{_libexecdir}/news/signcontrol
%{_libexecdir}/news/tdx-util
%{_libexecdir}/news/tally.control
%{_libexecdir}/news/overchan
%{_libexecdir}/news/sendinpaths
%{_libexecdir}/news/makehistory
%{_libexecdir}/news/nntpsend
%{_libexecdir}/news/mailpost
%{_libexecdir}/news/innfeed
%{_libexecdir}/news/ovdb_monitor
%{_libexecdir}/news/sendxbatches

%define filterdir %{_libexecdir}/news/filter
%dir %{filterdir}
%{filterdir}/filter_nnrpd.pl
%{filterdir}/nnrpd_access.pl
%{filterdir}/startup_innd.pl
%{filterdir}/nnrpd_auth.py*
%{filterdir}/nnrpd_access.py*
%{filterdir}/nnrpd_auth.pl
%{filterdir}/INN.py*
%{filterdir}/__pycache__/
%{filterdir}/nnrpd.py*
%{filterdir}/filter_innd.py*
%{filterdir}/nnrpd_dynamic.py*

%define authdir %{_libexecdir}/news/auth
%dir %{authdir}

%define passwddir %{authdir}/passwd
%dir %{passwddir}
%{passwddir}/auth_krb5
%{passwddir}/ckpasswd
%{passwddir}/radius

%define resolvdir %{authdir}/resolv
%dir %{resolvdir}
%{resolvdir}/domain
%{resolvdir}/ident

%define controldir %{_libexecdir}/news/control
%dir %{controldir}
%{controldir}/version.pl
%{controldir}/ihave.pl
%{controldir}/sendsys.pl
%{controldir}/sendme.pl
%{controldir}/checkgroups.pl
%{controldir}/senduuname.pl
%{controldir}/newgroup.pl
%{controldir}/rmgroup.pl

%define rnewsdir %{_libexecdir}/news/rnews.libexec
%dir %{rnewsdir}
%{rnewsdir}/encode
%{rnewsdir}/gunbatch
%{rnewsdir}/decode
%{rnewsdir}/bunbatch
%{rnewsdir}/c7unbatch

%{_libexecdir}/news/innshellvars.pl
%{_libexecdir}/news/innshellvars
%{_libexecdir}/news/innshellvars.tcl

%attr(0775,root,news) %dir %{_sharedstatedir}/news/http
%{_sharedstatedir}/news/http/innreport.css

%{perl_vendorlib}/INN

%defattr(-,news,news)
%dir /var/spool/news
%dir /var/spool/news/archive
%dir /var/spool/news/articles
%dir /var/spool/news/incoming
%dir /var/spool/news/incoming/bad
%dir /var/spool/news/innfeed
%dir /var/spool/news/outgoing
%dir /var/spool/news/overview
%dir /var/log/news
%dir /var/log/news/OLD
%dir /var/lib/news/tmp
%ghost %dir /run/news

%{_mandir}/man1/*
%exclude %{_mandir}/man1/inews.1*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}{,.*}

%files -n %{libhist}
%{_libdir}/lib%{name}hist.so.%{major_h}{,.*}

%files -n %{libsto}
%{_libdir}/libstorage.so.%{major_s}{,.*}

%files -n %{devname}
%{_includedir}/inn
%{_mandir}/man3/*
%{_libdir}/*.so

%files -n inews
%config(noreplace) %attr(-,news,news) %{_sysconfdir}/news/inn.conf
%{_bindir}/inews
%attr(0755,root,root) %{_libexecdir}/news/inews
%{_mandir}/man1/inews.1*
