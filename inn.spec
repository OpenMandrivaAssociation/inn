%define perl_version %(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)

%if %{_use_internal_dependency_generator}
%define __noautoreq 'perl\\(bigint.pl\\)|perl\\(ftp.pl\\)'
%else
%define _requires_exceptions perl(bigint.pl)\\|perl(ftp.pl)
%endif

Summary:	The InterNetNews (INN) system, a Usenet news server
Name:		inn
Version:	2.5.3
Release:	3
License:	GPLv2+
Group:		System/Servers
Url:		http://www.isc.org/products/INN/
Source0:	ftp://ftp.isc.org/isc/inn/%{name}-%{version}.tar.gz
Source1:	inn-default-active
Source2:	inn-default-distributions
Source3:	inn-default-newsgroups
Source4:	inn-cron-expire
Source5:	inn-cron-rnews
Source6:	inn-etc-nnrp.access
Source7:	inn-cron-nntpsend
Source8:	innd.init
Source10:	inn-faq.tar.bz2
Source20:	%{name}.rpmlintrc
Patch0:		inn-2.4.3.rh.patch
Patch1:		inn-2.4.1.perl.patch
Patch2:		inn-2.5.1.pie.patch
Patch3:		inn-2.5.2.posix.patch
Patch4:		inn-2.5.1.warn.patch
Patch5:		inn-2.5.1-makedbz.patch
Patch8:		inn-2.5.1-nologinshell.patch
Patch9:		inn-2.5.0-chown.patch
Patch10:	inn-redhat_build.patch
Patch11:	inn-shared.patch
Patch12:	inn-2.5.2-smp.patch
Patch13:	inn-2.5.3-flex.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	db-devel
BuildRequires:	krb5-devel
BuildRequires:	pam-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(ext2fs)
BuildRequires:	pkgconfig(openssl)
Requires(pre):	chkconfig
Requires(pre):	coreutils
Requires(pre):	grep
Requires(pre):	sed
Requires(pre):	rpm-helper
Requires:	cleanfeed
Requires:	perl = %{perl_version}
Requires:	sendmail-command

%description
INN (InterNetNews) is a complete system for serving Usenet news and/or
private newsfeeds.  INN includes innd, an NNTP (NetNews Transport
Protocol) server, and nnrpd, a newsreader that is spawned for each client. 
Both innd and nnrpd vary slightly from the NNTP protocol, but not in ways
that are easily noticed.

Install the inn package if you need a complete system for serving and
reading Usenet news.  You may also need to install inn-devel, if you are
going to use a separate program which interfaces to INN, like newsgate or
tin.

%package	devel
Summary:	The INN (InterNetNews) library
Group:		Development/C
Requires:	inn = %{version}

%description	devel
The inn-devel package contains the INN (InterNetNews) library, which
several programs that interface with INN need in order to work (for
example, newsgate and tin).

If you are installing a program which must interface with the INN
news system, you should install inn-devel.

%package -n	inews
Summary:	Sends Usenet articles to a local news server for distribution
Group:		System/Servers
Conflicts:	noffle

%description -n	inews
The inews program is used by some news programs (for example, inn and
trn) to post Usenet news articles to local news servers.  Inews reads an
article from a file or standard input, adds headers, performs some
consistency checks and then sends the article to the local news server
specified in the inn.conf file.

Install inews if you need a program for posting Usenet articles to local
news servers.

%prep
%setup -q -a 10
%apply_patches

find -type f | xargs perl -pi -e '@meuh = qw(LOCK_READ LOCK_WRITE LOCK_UNLOCK); foreach $a (@meuh) { s/\b$a\b/INN_$a/g }'
# lib64 fix
sed -i -e "s|/lib\b|/%{_lib}|g" m4/*.m4 configure*
autoreconf -fi

%build
%serverbuild
export CFLAGS="$CFLAGS -DHAVE_ET_COM_ERR_H -fPIC"

%configure2_5x \
	--prefix=/usr  \
	--libdir=%{_libdir} \
	--with-lib-dir=%{_libdir}/%{name} \
	--with-filter-dir=%{_libdir}/news/bin/filter \
	--with-control-dir=%{_libdir}/news/bin/control \
	--sysconfdir=/etc/news \
	--mandir=%{_mandir} \
	--libexecdir=%{_libdir}/%{name} \
	--with-log-dir=/var/log/news --with-spool-dir=/var/spool/news\
	--with-db-dir=/var/lib/news --with-run-dir=/var/run/news \
	--with-etc-dir=/etc/news --with-tmp-path=/var/spool/news/tmp \
	--with-perl --enable-shared --disable-static \
	--enable-tagged-hash --enable-merge-to-groups \
	--enable-ipv6 --with-libperl-dir=%{perl_vendorlib} \
	--with-news-user=news --with-news-group=news \
	--with-news-master=news --enable-pgp-verify \
	--with-openssl \
	--with-sendmail=/usr/sbin/sendmail \
	--with-berkeleydb=%{_prefix} \
	--with-http-dir=%{_sharedstatedir}/news/http

%make

%install
mkdir -p %{buildroot}
sed -i -e 's/^OWNER.*/OWNER = /; s/^ROWNER.*/ROWNER = /' Makefile.global

TMP_UID="`id -un`"
TMP_GID="`id -gn`"
sed -i -e "s|^NEWSUSER.*|NEWSUSER=${TMP_UID}|g" Makefile.global
sed -i -e "s|^NEWSGROUP.*|NEWSGROUP=${TMP_GID}|g" Makefile.global

%makeinstall_std

# -- Install man pages needed by suck et al.
mkdir -p %{buildroot}%{_includedir}/inn
for f in clibrary.h config.h
do
    install -c -m 0644 ./include/$f %{buildroot}%{_includedir}/inn
done

mkdir -p %{buildroot}/etc
mv %{buildroot}/usr/bin/rc.news %{buildroot}/etc

sed -i -e 's|%{_libdir}/inn/news/innshellvars|%{_bindir}/innshellvars|' %{buildroot}/etc/rc.news
chmod 755 %{buildroot}/etc/rc.news

touch %{buildroot}/var/lib/news/subscriptions
chmod 644 %{buildroot}/var/lib/news/subscriptions

install -m 644 %{SOURCE1} \
        %{buildroot}/var/lib/news/active
install -m 644 %{SOURCE2} \
        %{buildroot}/var/lib/news/distributions
install -m 644 %{SOURCE3} \
        %{buildroot}/var/lib/news/newsgroups

mkdir -p %{buildroot}/etc/cron.hourly %{buildroot}/etc/cron.daily
install -m755 %{SOURCE4} \
        %{buildroot}/etc/cron.daily/inn-cron-expire
install -m755 %{SOURCE5} \
        %{buildroot}/etc/cron.hourly/inn-cron-rnews
install -m755 %{SOURCE7} \
        %{buildroot}/etc/cron.hourly/inn-cron-nntpsend

install -m440 %{SOURCE6} \
        %{buildroot}/etc/news/nnrp.access

mkdir -p %{buildroot}/etc/rc.d/init.d/
install -m 755 %{SOURCE8} \
	%{buildroot}/etc/rc.d/init.d/innd

rm -f %{buildroot}/var/lib/news/history
touch %{buildroot}/var/lib/news/history
touch %{buildroot}/var/lib/news/.news.daily
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/usr/bin/makehistory \
	-a %{buildroot}/var/lib/news/active \
	-r -f %{buildroot}/var/lib/news/history || :
chmod 644 %{buildroot}/var/lib/news/*
chmod 644 %{buildroot}/var/lib/news/.news.daily

mkdir -p %{buildroot}/var/spool/news/tmp

# we get this from cleanfeed
# (sb) true - but it's not being found by innd - fix this
rm -f %{buildroot}/%{_libdir}/news/bin/filter/filter_innd.pl
pushd %{buildroot}/%{_libdir}/news/bin/filter
ln -sf ../control/filter_innd.pl . 
popd

# fix location of real library files
#mv %{buildroot}%{_libdir}/{inn/lib{inn,storage}.a,/}

#Fix perms in sample directory to avoid bogus dependencies
find samples -name "*.in" -exec chmod a-x {} \;

# (sb) doc install conflicts with rpm %%doc, even when config is setup
# correctly. Just rm these files and let %%doc take care of it
rm -fr %{buildroot}/%{_usr}/doc

# (sb) a portion of the header files are in /usr/include, while the rest
# are in /usr/include/inn - paths.h conflicts with glibc-devel
# right now inn-devel isn't used for anything, nor do the other header
# files seem to be looking for them a directory up - move them
#mv %{buildroot}/%{_includedir}/*.h %{buildroot}/%{_includedir}/inn

# (sb) file mode now prevents strip from working?
chmod u+w %{buildroot}/%{_bindir}/*
chmod u+w %{buildroot}/%{_bindir}/auth/resolv/*
chmod u+w %{buildroot}/%{_bindir}/auth/passwd/*
chmod u+w %{buildroot}/%{_bindir}/rnews.libexec/*

%post
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

%triggerin -- sysklogd
if [ -f /etc/syslog.conf ]; then
  if grep -q "# News logging" /etc/syslog.conf; then
sed -i -e "s!mail.none;authpriv.none!mail.none;news.none;authpriv.none!; \
	     s!/var/log/news/info!/var/log/news/news.notice!; \
	     s!/var/log/news/errors!/var/log/news/news.err!; \
	     s!/var/log/news/warnings!/var/log/news/news.crit!; \
	     s!^news.err!news.=err!; \
	     s!^news.=warn!news.=crit!; " /etc/syslog.conf 
	else
	cat <<EOF >> /etc/syslog.conf
# News logging
news.=debug;news.=info;news.=notice                             -/var/log/news/news.notice
news.=crit                                                      -/var/log/news/news.crit
news.err                                                        -/var/log/news/news.err
EOF
    fi
  if [ -f /var/run/syslog.pid ]; then
    kill -HUP `cat /var/run/syslog.pid` 2> /dev/null ||:
  fi
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
%defattr(-,news,news)
%dir %{_sysconfdir}/news
%attr(775,news,news) %dir /var/spool/news
%attr(775,news,news) %dir /var/spool/news/articles
%attr(775,news,news) %dir /var/spool/news/overview
%attr(775,news,news) %dir /var/spool/news/archive
%attr(775,news,news) %dir /var/spool/news/incoming
%attr(775,news,news) %dir /var/spool/news/incoming/bad
%attr(775,news,news) %dir /var/spool/news/outgoing
%attr(775,news,news) %dir /var/spool/news/innfeed
%attr(770,news,news) %dir /var/spool/news/tmp
%attr(770,news,news) %dir /var/log/news
/var/log/news/OLD
%attr(770,news,news) %dir /var/lib/news
%attr(770,news,news) %dir /var/run/news

%attr(-,root,root) %doc HACKING LICENSE MANIFEST TODO
%attr(-,root,root) %doc README* ChangeLog CONTRIBUTORS INSTALL NEWS
%attr(-,root,root) %doc faq
%attr(-,root,root) %doc doc/hook* doc/config*
%attr(-,root,root) %doc doc/sample-control doc/GPL doc/history

%defattr(755,root,root)
%{_prefix}/com/news/http/innreport.css

%dir %{_libdir}/news/bin/control
%dir %{_libdir}/news/bin/filter
%{_libdir}/news/bin/filter/filter_innd.pl
%{_libdir}/news/bin/filter/nnrpd_auth.pl
%{_libdir}/news/bin/filter/startup_innd.pl
%{_libdir}/news/bin/filter/INN.py
%{_libdir}/news/bin/filter/filter_nnrpd.pl
%{_libdir}/news/bin/filter/nnrpd_dynamic.py
%{_libdir}/news/bin/filter/nnrpd_auth.py
%{_libdir}/news/bin/filter/nnrpd_access.pl
%{_libdir}/news/bin/filter/nnrpd_access.py
%{_libdir}/news/bin/filter/nnrpd.py
%{_libdir}/news/bin/filter/filter_innd.py
%{_libdir}/news/bin/control/sendsys.pl
%{_libdir}/news/bin/control/rmgroup.pl
%{_libdir}/news/bin/control/newgroup.pl
%{_libdir}/news/bin/control/ihave.pl
%{_libdir}/news/bin/control/sendme.pl
%{_libdir}/news/bin/control/checkgroups.pl
%{_libdir}/news/bin/control/version.pl
%{_libdir}/news/bin/control/senduuname.pl
%dir %{perl_vendorlib}/INN
%dir %{perl_vendorlib}/INN/Utils
%{perl_vendorlib}/INN/Config.pm
%{perl_vendorlib}/INN/Utils/Shlock.pm
%{_bindir}/scanspool
%{_bindir}/nntpsend
%{_bindir}/send-ihave
%{_bindir}/send-nntp
%{_bindir}/send-uucp
%{_bindir}/perl-nocem
%{_bindir}/shrinkfile
%{_bindir}/tdx-util
%{_bindir}/convdate
%{_bindir}/innbind
%{_bindir}/getlist
%{_bindir}/buffindexed_d
%{_bindir}/innreport_inn.pm
%config(noreplace) %{_bindir}/innshellvars.pl
%{_bindir}/archive
%{_bindir}/pullnews
%attr(6550,uucp,news) %{_bindir}/rnews
%dir %{_bindir}/rnews.libexec
%{_bindir}/rnews.libexec/gunbatch
%{_bindir}/rnews.libexec/c7unbatch
%{_bindir}/rnews.libexec/decode
%{_bindir}/rnews.libexec/encode
%{_bindir}/rnews.libexec/bunbatch
%{_bindir}/sendxbatches
%{_bindir}/nnrpd
%{_bindir}/filechan
%{_bindir}/innxmit
%{_bindir}/tinyleaf
%{_bindir}/cnfsstat
%{_bindir}/ovdb_stat
%{_bindir}/ninpaths
%{_bindir}/innfeed
%{_bindir}/signcontrol
%{_bindir}/sendinpaths
%{_bindir}/tally.control
%dir %{_bindir}/auth/resolv
%dir %{_bindir}/auth/passwd
%{_bindir}/auth/passwd/ckpasswd
%{_bindir}/auth/passwd/radius
%{_bindir}/auth/resolv/domain
%{_bindir}/auth/resolv/ident
%{_bindir}/imapfeed
%{_bindir}/innupgrade
%{_bindir}/expireover
%{_bindir}/makehistory
%{_bindir}/writelog
%{_bindir}/simpleftp
%{_bindir}/grephistory
%{_bindir}/sm
%{_bindir}/mod-active
%{_bindir}/mailpost
%{_bindir}/innconfval
%{_bindir}/procbatch
%{_bindir}/cvtbatch
%config(noreplace) %{_bindir}/innshellvars.tcl
%{_bindir}/cnfsheadconf
%{_bindir}/pgpverify
%{_bindir}/actsync
%{_bindir}/nntpget
%{_bindir}/innreport
%{_bindir}/ovdb_monitor
%{_bindir}/buffchan
%{_bindir}/actsyncd
%{_bindir}/controlchan
%config(noreplace) %{_bindir}/innshellvars
%{_bindir}/shlock
%{_bindir}/news.daily
%{_bindir}/docheckgroups
%{_bindir}/ovdb_server
%{_bindir}/ovdb_init
%{_bindir}/scanlogs
%{_bindir}/inncheck
%{_bindir}/controlbatch
%{_bindir}/actmerge
%{_bindir}/innd
%{_bindir}/expire
%{_bindir}/prunehistory
%{_bindir}/makedbz
%{_bindir}/innstat
%{_bindir}/fastrm
%{_bindir}/innxbatch
%{_bindir}/ctlinnd
%{_bindir}/innmail
%{_bindir}/innwatch
%{_bindir}/news2mail
%{_bindir}/inndf
%{_bindir}/batcher
%{_bindir}/expirerm
%{_bindir}/overchan
%config(noreplace) %attr(755,root,root) %{_initrddir}/innd
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/actsync.cfg
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/actsync.ign
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/buffindexed.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/control.ctl
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/control.ctl.local
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/cycbuff.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/distrib.pats
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/distributions
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/expire.ctl
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/incoming.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innfeed.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innreport.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innshellvars.local
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innshellvars.pl.local
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innshellvars.tcl.local
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/innwatch.ctl
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/localgroups
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/moderators
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/motd.innd
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/motd.nnrpd
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/news2mail.cf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/newsfeeds
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/nnrp.access
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/nnrpd.track
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/nntpsend.ctl
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/nocem.ctl
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/ovdb.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/passwd.nntp
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/radius.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/readers.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/send-uucp.cf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/storage.conf
%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/subscriptions
%attr(640,uucp,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/news/inn.conf
%{_sysconfdir}/cron.hourly/inn-cron-nntpsend
%config(noreplace) %attr(755,root,root) %{_sysconfdir}/cron.hourly/inn-cron-rnews
%attr(755,root,news) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/rc.news
%{_sysconfdir}/cron.daily/inn-cron-expire
%attr(640,news,news) %config(noreplace) /var/lib/news/active
%attr(640,news,news) %config(noreplace) /var/lib/news/.news.daily
%attr(640,news,news) %config(noreplace) /var/lib/news/active.times
%attr(640,news,news) %config(noreplace) /var/lib/news/subscriptions
%attr(640,news,news) %config(noreplace) /var/lib/news/history
%attr(640,news,news) %config(noreplace) /var/lib/news/distributions
%attr(640,news,news) %config(noreplace) /var/lib/news/newsgroups
%attr(644,root,root) %{_mandir}/man1/convdate.1*
%attr(644,root,root) %{_mandir}/man1/fastrm.1*
%attr(644,root,root) %{_mandir}/man1/getlist.1*
%attr(644,root,root) %{_mandir}/man1/grephistory.1*
%attr(644,root,root) %{_mandir}/man1/innconfval.1*
%attr(644,root,root) %{_mandir}/man1/innmail.1*
%attr(644,root,root) %{_mandir}/man1/nntpget.1*
%attr(644,root,root) %{_mandir}/man1/pgpverify.1*
%attr(644,root,root) %{_mandir}/man1/pullnews.1*
%attr(644,root,root) %{_mandir}/man1/rnews.1*
%attr(644,root,root) %{_mandir}/man1/shlock.1*
%attr(644,root,root) %{_mandir}/man1/shrinkfile.1*
%attr(644,root,root) %{_mandir}/man1/simpleftp.1*
%attr(644,root,root) %{_mandir}/man1/sm.1*
%attr(644,root,root) %{_mandir}/man5/active.5*
%attr(644,root,root) %{_mandir}/man5/active.times.5*
%attr(644,root,root) %{_mandir}/man5/buffindexed.conf.5*
%attr(644,root,root) %{_mandir}/man5/control.ctl.5*
%attr(644,root,root) %{_mandir}/man5/cycbuff.conf.5*
%attr(644,root,root) %{_mandir}/man5/distrib.pats.5*
%attr(644,root,root) %{_mandir}/man5/distributions.5*
%attr(644,root,root) %{_mandir}/man5/expire.ctl.5*
%attr(644,root,root) %{_mandir}/man5/history.5*
%attr(644,root,root) %{_mandir}/man5/incoming.conf.5*
%attr(644,root,root) %{_mandir}/man5/inn.conf.5*
%attr(644,root,root) %{_mandir}/man5/innfeed.conf.5*
%attr(644,root,root) %{_mandir}/man5/innwatch.ctl.5*
%attr(644,root,root) %{_mandir}/man5/localgroups.5*
%attr(644,root,root) %{_mandir}/man5/moderators.5*
%attr(644,root,root) %{_mandir}/man5/motd.innd.5*
%attr(644,root,root) %{_mandir}/man5/motd.news.5*
%attr(644,root,root) %{_mandir}/man5/motd.nnrpd.5*
%attr(644,root,root) %{_mandir}/man5/newsfeeds.5*
%attr(644,root,root) %{_mandir}/man5/newsgroups.5*
%attr(644,root,root) %{_mandir}/man5/newslog.5*
%attr(644,root,root) %{_mandir}/man5/nnrpd.track.5*
%attr(644,root,root) %{_mandir}/man5/nntpsend.ctl.5*
%attr(644,root,root) %{_mandir}/man5/nocem.ctl.5*
%attr(644,root,root) %{_mandir}/man5/ovdb.5*
%attr(644,root,root) %{_mandir}/man5/passwd.nntp.5*
%attr(644,root,root) %{_mandir}/man5/radius.conf.5*
%attr(644,root,root) %{_mandir}/man5/readers.conf.5*
%attr(644,root,root) %{_mandir}/man5/storage.conf.5*
%attr(644,root,root) %{_mandir}/man5/subscriptions.5*
%attr(644,root,root) %{_mandir}/man8/actsync.8*
%attr(644,root,root) %{_mandir}/man8/actsyncd.8*
%attr(644,root,root) %{_mandir}/man8/archive.8*
%attr(644,root,root) %{_mandir}/man8/batcher.8*
%attr(644,root,root) %{_mandir}/man8/buffchan.8*
%attr(644,root,root) %{_mandir}/man8/ckpasswd.8*
%attr(644,root,root) %{_mandir}/man8/cnfsheadconf.8*
%attr(644,root,root) %{_mandir}/man8/cnfsstat.8*
%attr(644,root,root) %{_mandir}/man8/controlchan.8*
%attr(644,root,root) %{_mandir}/man8/ctlinnd.8*
%attr(644,root,root) %{_mandir}/man8/cvtbatch.8*
%attr(644,root,root) %{_mandir}/man8/docheckgroups.8*
%attr(644,root,root) %{_mandir}/man8/domain.8*
%attr(644,root,root) %{_mandir}/man8/expire.8*
%attr(644,root,root) %{_mandir}/man8/expireover.8*
%attr(644,root,root) %{_mandir}/man8/expirerm.8*
%attr(644,root,root) %{_mandir}/man8/filechan.8*
%attr(644,root,root) %{_mandir}/man8/ident.8*
%attr(644,root,root) %{_mandir}/man8/imapfeed.8*
%attr(644,root,root) %{_mandir}/man8/innbind.8*
%attr(644,root,root) %{_mandir}/man8/inncheck.8*
%attr(644,root,root) %{_mandir}/man8/innd.8*
%attr(644,root,root) %{_mandir}/man8/inndf.8*
%attr(644,root,root) %{_mandir}/man8/innfeed.8*
%attr(644,root,root) %{_mandir}/man8/innreport.8*
%attr(644,root,root) %{_mandir}/man8/innstat.8*
%attr(644,root,root) %{_mandir}/man8/innupgrade.8*
%attr(644,root,root) %{_mandir}/man8/innwatch.8*
%attr(644,root,root) %{_mandir}/man8/innxbatch.8*
%attr(644,root,root) %{_mandir}/man8/innxmit.8*
%attr(644,root,root) %{_mandir}/man8/inpaths.8*
%attr(644,root,root) %{_mandir}/man8/mailpost.8*
%attr(644,root,root) %{_mandir}/man8/makedbz.8*
%attr(644,root,root) %{_mandir}/man8/makehistory.8*
%attr(644,root,root) %{_mandir}/man8/mod-active.8*
%attr(644,root,root) %{_mandir}/man8/news.daily.8*
%attr(644,root,root) %{_mandir}/man8/news2mail.8*
%attr(644,root,root) %{_mandir}/man8/ninpaths.8*
%attr(644,root,root) %{_mandir}/man8/nnrpd.8*
%attr(644,root,root) %{_mandir}/man8/nntpsend.8*
%attr(644,root,root) %{_mandir}/man8/ovdb_init.8*
%attr(644,root,root) %{_mandir}/man8/ovdb_monitor.8*
%attr(644,root,root) %{_mandir}/man8/ovdb_server.8*
%attr(644,root,root) %{_mandir}/man8/ovdb_stat.8*
%attr(644,root,root) %{_mandir}/man8/overchan.8*
%attr(644,root,root) %{_mandir}/man8/perl-nocem.8*
%attr(644,root,root) %{_mandir}/man8/procbatch.8*
%attr(644,root,root) %{_mandir}/man8/prunehistory.8*
%attr(644,root,root) %{_mandir}/man8/radius.8*
%attr(644,root,root) %{_mandir}/man8/rc.news.8*
%attr(644,root,root) %{_mandir}/man8/scanlogs.8*
%attr(644,root,root) %{_mandir}/man8/scanspool.8*
%attr(644,root,root) %{_mandir}/man8/send-nntp.8*
%attr(644,root,root) %{_mandir}/man8/send-uucp.8*
%attr(644,root,root) %{_mandir}/man8/sendinpaths.8*
%attr(644,root,root) %{_mandir}/man8/tally.control.8*
%attr(644,root,root) %{_mandir}/man8/tdx-util.8*
%attr(644,root,root) %{_mandir}/man8/tinyleaf.8*
%attr(644,root,root) %{_mandir}/man8/writelog.8*

%files devel
%defattr(-,root,root)
%{_mandir}/man3/*
%dir %{_includedir}/%{name}
%defattr(644,root,root)
%{_libdir}/libinnhist.a
%{_libdir}/libinn.a
%{_libdir}/libstorage.a
%{_includedir}/inn/clibrary.h
%{_includedir}/inn/inndcomm.h
%{_includedir}/inn/vector.h
%{_includedir}/inn/dbz.h
%{_includedir}/inn/confparse.h
%{_includedir}/inn/storage.h
%{_includedir}/inn/timer.h
%{_includedir}/inn/mmap.h
%{_includedir}/inn/ov.h
%{_includedir}/inn/md5.h
%{_includedir}/inn/network.h
%{_includedir}/inn/tst.h
%{_includedir}/inn/history.h
%{_includedir}/inn/libinn.h
%{_includedir}/inn/nntp.h
%{_includedir}/inn/version.h
%{_includedir}/inn/system.h
%{_includedir}/inn/config.h
%{_includedir}/inn/sequence.h
%{_includedir}/inn/defines.h
%{_includedir}/inn/innconf.h
%{_includedir}/inn/qio.h
%{_includedir}/inn/paths.h
%{_includedir}/inn/options.h
%{_includedir}/inn/list.h
%{_includedir}/inn/buffer.h
%{_includedir}/inn/wire.h
%{_includedir}/inn/utility.h
%{_includedir}/inn/overview.h
%{_includedir}/inn/hashtab.h
%{_includedir}/inn/messages.h
%{_includedir}/inn/dispatch.h
%{_includedir}/inn/newsuser.h

%files -n inews
%attr(755,root,root) /usr/bin/inews
%attr(644,root,root) %{_mandir}/man1/inews*


