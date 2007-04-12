%define version 2.4.3
%define release %mkrel 6

%define perl_version %(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)

Summary:	The InterNetNews (INN) system, a Usenet news server
Name:		inn
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
Url:		http://www.isc.org/products/INN/
Source0:	ftp://ftp.isc.org/isc/inn/inn-%{version}.tar.bz2
Source1:	inn-default-active
Source2:	inn-default-distributions
Source3:	inn-default-newsgroups
Source4:	inn-cron-expire
Source5:	inn-cron-rnews
Source6:	inn-etc-nnrp.access
Source7:	inn-cron-nntpsend
Source8:	innd.init
Source10:	inn-faq.tar.bz2
Patch0:		inn-2.4.0-rh.patch
Patch2:		inn-2.4.2-fix-make-install.patch
Patch3:		inn-2.4.3-lib64.patch
Patch4:		inn-2.4.3-use-db4.patch
BuildRequires:	autoconf2.1 bison flex
BuildRequires:  openssl-devel perl-devel e2fsprogs-devel
BuildRequires:	db4.2-devel
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires(pre):	/sbin/chkconfig grep coreutils sed rpm-helper
Requires:	cleanfeed, perl = %{perl_version}
Requires:	sendmail-command
Conflicts:	echelog jabber2

%define _requires_exceptions perl(bigint.pl)\\|perl(ftp.pl)

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
%patch0 -p1 -b .redhat
%patch2 -p1 -b .make_install
%patch3 -p1 -b .lib64
%patch4 -p1 -b .use-db4
autoconf

find -type f | xargs perl -pi -e '@meuh = qw(LOCK_READ LOCK_WRITE LOCK_UNLOCK); foreach $a (@meuh) { s/\b$a\b/INN_$a/g }'

%build
%serverbuild
export CFLAGS="$CFLAGS -DHAVE_ET_COM_ERR_H"

rm -f config.cache
libtoolize --copy --force
./configure --prefix=/usr  \
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
	--with-perl --enable-shared --enable-static \
	--enable-tagged-hash --enable-merge-to-groups \
	--with-news-user=news --with-news-group=news \
	--with-news-master=news --enable-pgp-verify \
	--with-openssl \
	--with-sendmail=/usr/sbin/sendmail \
	--with-berkeleydb=/usr/include/db4

%make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
perl -pi -e 's/^OWNER.*/OWNER = /; s/^ROWNER.*/ROWNER = /' Makefile.global
make install DESTDIR=$RPM_BUILD_ROOT

# -- Install man pages needed by suck et al.
mkdir -p $RPM_BUILD_ROOT/usr/include/inn
for f in clibrary.h config.h dbz.h libinn.h storage.h
do
    install -c -m 0644 ./include/$f $RPM_BUILD_ROOT/usr/include/inn
done

mkdir -p $RPM_BUILD_ROOT/etc
mv $RPM_BUILD_ROOT/usr/bin/rc.news $RPM_BUILD_ROOT/etc
chmod 755 $RPM_BUILD_ROOT/etc/rc.news

touch $RPM_BUILD_ROOT/var/lib/news/subscriptions
chmod 644 $RPM_BUILD_ROOT/var/lib/news/subscriptions

install -m 644 %{SOURCE1} \
        $RPM_BUILD_ROOT/var/lib/news/active
install -m 644 %{SOURCE2} \
        $RPM_BUILD_ROOT/var/lib/news/distributions
install -m 644 %{SOURCE3} \
        $RPM_BUILD_ROOT/var/lib/news/newsgroups

mkdir -p $RPM_BUILD_ROOT/etc/cron.hourly $RPM_BUILD_ROOT/etc/cron.daily
install -m755 %{SOURCE4} \
        $RPM_BUILD_ROOT/etc/cron.daily/inn-cron-expire
install -m755 %{SOURCE5} \
        $RPM_BUILD_ROOT/etc/cron.hourly/inn-cron-rnews
install -m755 %{SOURCE7} \
        $RPM_BUILD_ROOT/etc/cron.hourly/inn-cron-nntpsend

install -m440 %{SOURCE6} \
        $RPM_BUILD_ROOT/etc/news/nnrp.access

mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d/
install -m 755 %{SOURCE8} \
	$RPM_BUILD_ROOT/etc/rc.d/init.d/innd

rm -f $RPM_BUILD_ROOT/var/lib/news/history
touch $RPM_BUILD_ROOT/var/lib/news/history
touch $RPM_BUILD_ROOT/var/lib/news/.news.daily
LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT/usr/bin/makehistory \
	-a $RPM_BUILD_ROOT/var/lib/news/active \
	-r -f $RPM_BUILD_ROOT/var/lib/news/history || :
chmod 644 $RPM_BUILD_ROOT/var/lib/news/*
chmod 644 $RPM_BUILD_ROOT/var/lib/news/.news.daily

mkdir -p $RPM_BUILD_ROOT/var/spool/news/tmp

# we get this from cleanfeed
# (sb) true - but it's not being found by innd - fix this
rm -f $RPM_BUILD_ROOT/%{_libdir}/news/bin/filter/filter_innd.pl
pushd $RPM_BUILD_ROOT/%{_libdir}/news/bin/filter
ln -sf ../control/filter_innd.pl . 
popd

# fix location of real library files
mv $RPM_BUILD_ROOT%{_libdir}/{inn/lib{inn,storage}.a,/}

#Fix perms in sample directory to avoid bogus dependencies
find samples -name "*.in" -exec chmod a-x {} \;

# (sb) doc install conflicts with rpm %%doc, even when config is setup
# correctly. Just rm these files and let %%doc take care of it
rm -fr $RPM_BUILD_ROOT/%{_usr}/doc

# (sb) a portion of the header files are in /usr/include, while the rest
# are in /usr/include/inn - paths.h conflicts with glibc-devel
# right now inn-devel isn't used for anything, nor do the other header
# files seem to be looking for them a directory up - move them
mv $RPM_BUILD_ROOT/%{_includedir}/*.h $RPM_BUILD_ROOT/%{_includedir}/inn

#Build filelist
echo "%defattr(-,news,news)" > files.list
find $RPM_BUILD_ROOT -type f -or -type l | \
	sed -e "s|$RPM_BUILD_ROOT||g" | \
	sed 's|^%{_initrddir}/innd|%config(noreplace) %attr(755,root,root) &|' | \
	sed 's|^/etc/news/inn.conf|%attr(640,uucp,news) %config(noreplace) %verify(not size mtime md5) &|' | \
	sed 's|^/etc/news|%attr(640,root,news) %config(noreplace) %verify(not size mtime md5) &|' | \
	sed 's|^/etc/rc.news|%attr(755,root,news) %config(noreplace) %verify(not size mtime md5) &|' | \
	sed 's|^/etc/init.d|%attr(755,root,root) %config(noreplace) %verify(not size mtime md5) &|' | \
	sed 's|^/etc/cron.hourly/inn-cron-rnews|%config(noreplace) %attr(755,root,root) &|' | \
	sed 's|^/var/lib/news/|%attr(640,news,news) %config(noreplace) &|' | \
	sed 's|.*innshellvar|%config(noreplace) &|' | \
	sed 's|/var/log/news|%ghost &|' | \
	sed 's|/usr/bin/inndstart|%attr(4750,root,news) &|' | \
	sed 's|/usr/bin/startinnfeed$|%attr(4550,root,news) &|' | \
	sed 's|/usr/bin/rnews$|%attr(6550,uucp,news) /usr/bin/rnews|' |
	sed '/%attr(4550,uucp,news)/a\
%defattr(755,root,root)' > files.list

(echo "%defattr(755,root,root)" ; grep -v inews files.list | \
	egrep -v "\.(h|so|a|la)$" | \
	grep -v "/man/") > files.main
echo "%defattr(644,root,root)" > files.devel
egrep "\.(h|so|a|la)$" files.list >> files.devel
echo "%attr(-,root,root)" >> files.main
find $RPM_BUILD_ROOT%{_mandir}/man[158] -type f | \
	sed -e "s|$RPM_BUILD_ROOT||g" | \
	sed -e "s|\.[158]|&.bz2|g" | \
	grep -v inews >> files.main

# (sb) file mode now prevents strip from working?
chmod u+w $RPM_BUILD_ROOT/%{_bindir}/*
chmod u+w $RPM_BUILD_ROOT/%{_bindir}/auth/resolv/*
chmod u+w $RPM_BUILD_ROOT/%{_bindir}/auth/passwd/*
chmod u+w $RPM_BUILD_ROOT/%{_bindir}/rnews.libexec/*

%clean
rm -rf $RPM_BUILD_ROOT
rm -f files.list files.main files.devel files.inews

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
perl -pi -e "s!mail.none;authpriv.none!mail.none;news.none;authpriv.none!; \
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

%files -f files.main
%defattr(-,news,news)
%dir %{_libdir}/%{name}
%dir %{_libdir}/news
%dir %{_libdir}/news/bin
%dir %{_libdir}/news/bin/control
%dir %{_libdir}/news/bin/filter
%dir %{_bindir}/rnews.libexec
%dir %{_bindir}/auth
%dir %{_bindir}/auth/resolv
%dir %{_bindir}/auth/passwd
%dir %{_sysconfdir}/news
%dir /var/spool/news
%dir /var/spool/news/articles
%dir /var/spool/news/overview
%dir /var/spool/news/archive
%attr(775,news,news) %dir /var/spool/news/incoming
%attr(775,news,news) %dir /var/spool/news/incoming/bad
%dir /var/spool/news/outgoing
%dir /var/spool/news/innfeed
%attr(770,news,news) %dir /var/spool/news/tmp
%attr(770,news,news) %dir /var/log/news
%dir /var/log/news/OLD
%attr(770,news,news) %dir /var/lib/news
%attr(770,news,news) %dir /var/run/news

%attr(-,root,root) %doc HACKING LICENSE MANIFEST TODO
%attr(-,root,root) %doc README* ChangeLog CONTRIBUTORS INSTALL NEWS
%attr(-,root,root) %doc faq
%attr(-,root,root) %doc doc/hook* doc/config* doc/compliance-nntp 
%attr(-,root,root) %doc doc/sample-control doc/GPL doc/history

%files devel -f files.devel
%defattr(-,root,root)
%{_mandir}/man3/*
%dir %{_includedir}/%{name}

%files -n inews
%defattr(-,root,root)
%attr(755,root,root) /usr/bin/inews
%{_mandir}/man1/inews*

