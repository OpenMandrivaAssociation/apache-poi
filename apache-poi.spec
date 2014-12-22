%{?_javapackages_macros:%_javapackages_macros}
%global reldate 20140818
%global rcver %{nil}

Name:           apache-poi
Version:        3.10.1
Release:        1.1
Summary:        The Java API for Microsoft Documents

Group:          Development/Java
License:        ASL 2.0
URL:            http://poi.apache.org/
Source0:        http://www.apache.org/dist/poi/release/src/poi-src-%{version}-%{reldate}.tar.gz
#Source0:        http://www.apache.org/dist/poi/dev/src/poi-src-%{version}%{?rcver}-%{reldate}.tar.gz
Source1:        Office-Open-XML-1st-edition-Part4-PDF.zip
Source2:        http://repo2.maven.org/maven2/org/apache/poi/poi/%{version}/poi-%{version}.pom
Source3:        http://repo2.maven.org/maven2/org/apache/poi/poi-examples/%{version}/poi-examples-%{version}.pom
Source4:        http://repo2.maven.org/maven2/org/apache/poi/poi-excelant/%{version}/poi-excelant-%{version}.pom
Source5:        http://repo2.maven.org/maven2/org/apache/poi/poi-ooxml/%{version}/poi-ooxml-%{version}.pom
Source6:        http://repo2.maven.org/maven2/org/apache/poi/poi-ooxml-schemas/%{version}/poi-ooxml-schemas-%{version}.pom
Source7:        http://repo2.maven.org/maven2/org/apache/poi/poi-scratchpad/%{version}/poi-scratchpad-%{version}.pom
Source100:	apache-poi.rpmlintrc
#Force compile of xsds if disconnected
Patch1:         %{name}-compile-xsds.patch
Patch2:         %{name}-build.patch
BuildArch:      noarch

BuildRequires:  jpackage-utils
BuildRequires:  java-devel >= 1:1.6.0
BuildRequires:  ant-junit
BuildRequires:  dom4j
BuildRequires:  apache-commons-logging
BuildRequires:  junit
#Fonts for testing
BuildRequires:  fontconfig
BuildRequires:	fonts-ttf-liberation
BuildRequires:  jacoco
BuildRequires:  log4j
BuildRequires:  xmlbeans

Requires:       jpackage-utils
Requires:       java >= 1:1.6.0
Requires:       dom4j
Requires:       apache-commons-logging
Requires:       log4j
Requires:       xmlbeans

%description
The Apache POI Project's mission is to create and maintain Java APIs for
manipulating various file formats based upon the Office Open XML standards
(OOXML) and Microsoft's OLE 2 Compound Document format (OLE2). In short, you
can read and write MS Excel files using Java. In addition, you can read and
write MS Word and MS PowerPoint files using Java. Apache POI is your Java
Excel solution (for Excel 97-2008). We have a complete API for porting other
OOXML and OLE2 formats and welcome others to participate.

OLE2 files include most Microsoft Office files such as XLS, DOC, and PPT as
well as MFC serialization API based file formats. The project provides APIs
for the OLE2 Filesystem (POIFS) and OLE2 Document Properties (HPSF).

Office OpenXML Format is the new standards based XML file format found in
Microsoft Office 2007 and 2008. This includes XLSX, DOCX and PPTX. The
project provides a low level API to support the Open Packaging Conventions
using openxml4j.

For each MS Office application there exists a component module that attempts
to provide a common high level Java API to both OLE2 and OOXML document
formats. This is most developed for Excel workbooks (SS=HSSF+XSSF). Work is
progressing for Word documents (HWPF+XWPF) and PowerPoint presentations
(HSLF+XSLF).

The project has recently added support for Outlook (HSMF). Microsoft opened
the specifications to this format in October 2007. We would welcome
contributions.

There are also projects for Visio (HDGF) and Publisher (HPBF). 


%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.


%package manual
Summary:        Manual for %{name}
Group:          Documentation
Requires:       jpackage-utils
Requires:       %{name}-javadoc = %{version}-%{release}

%description manual
The manual for %{name}.


%prep
%setup -q -n poi-%{version}%{?rcver}
%patch1 -p1 -b .compile-xsds
%patch2 -p1 -b .build
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;
mkdir lib ooxml-lib
build-jar-repository -s -p lib ant commons-codec commons-logging jacoco junit log4j
build-jar-repository -s -p ooxml-lib dom4j xmlbeans/xbean
#Unpack the XMLSchema
pushd ooxml-lib
unzip "%SOURCE1" OfficeOpenXML-XMLSchema.zip
popd


%build
cat > build.properties <<'EOF'
main.ant.jar=lib/ant.jar
main.commons-codec.jar=lib/commons-codec.jar
main.commons-logging.jar=lib/commons-logging.jar
main.log4j.jar=lib/log4j.jar
main.junit.jar=lib/junit.jar
ooxml.dom4j.jar=ooxml-lib/dom4j.jar
ooxml.xmlbeans23.jar=ooxml-lib/xmlbeans_xbean.jar
ooxml.xmlbeans26.jar=ooxml-lib/xmlbeans_xbean.jar
disconnected=1
DSTAMP=%{reldate}
EOF
export ANT_OPTS="-Xmx768m"
ant -propertyfile build.properties compile-ooxml-xsds jar


%install
mkdir -p $RPM_BUILD_ROOT%{_javadir}/poi
mkdir -p $RPM_BUILD_ROOT%{_mavenpomdir}
cd build/dist
for jar in *.jar
do
  jarname=${jar/-%{version}*.jar/}
  cp -p ${jar} $RPM_BUILD_ROOT%{_javadir}/poi/apache-${jarname}.jar
  ln -s apache-${jarname}.jar $RPM_BUILD_ROOT%{_javadir}/poi/${jarname}.jar
  #pom
  cp -p %{_sourcedir}/${jarname}-%{version}*.pom \
        $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.poi-${jarname}.pom
  %add_maven_depmap JPP.poi-${jarname}.pom poi/${jarname}.jar
done
cd -

#javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}
cp -pr docs/apidocs $RPM_BUILD_ROOT%{_javadocdir}/%{name}
#Don't copy for manual
rm -rf docs/apidocs 

#manual - Link to javadoc location
ln -s ../../javadoc/%{name} docs/apidocs


%check
# To enable 8-bit character tests
export LANG=en_US.UTF-8
# Ignore test failures for now
ant -propertyfile build.properties test || :


%files -f build/dist/.mfiles
%doc KEYS LICENSE NOTICE
%dir %{_javadir}/poi
 %{_javadir}/poi/apache-poi*.jar

%files javadoc
%doc LICENSE
%{_javadocdir}/%{name}

%files manual
%doc LICENSE docs/*


%changelog
* Thu Sep 4 2014 Orion Poplawski <orion@cora.nwra.com> - 3.10.1-1
- Update to 3.10.1 (Bug 1138135: CVE-2014-3574 CVE-2014-3529)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Feb 24 2014 Orion Poplawski <orion@cora.nwra.com> - 3.10-1
- Update to 3.10

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jun 12 2013 Orion Poplawski <orion@cora.nwra.com> - 3.9-1
- Update to 3.9 final
- Install all jars and add poms for each
- Cleanup and update spec

* Fri Apr 05 2013 Karsten Hopp <karsten@redhat.com> 3.8-5
- drop excludearch ppc64

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Orion Poplawski <orion@cora.nwra.com> - 3.8-2
- Add patch to fix compilation with JDK 1.7

* Thu May 10 2012 Orion Poplawski <orion@cora.nwra.com> - 3.8-1
- Update to 3.8 final
- Add patch to fix CVE-2012-0213 (bugs 799078, 820788)

* Thu Jan 5 2012 Orion Poplawski <orion@cora.nwra.com> - 3.8-0.3.beta5
- Update to 3.8-beta5

* Fri Jul 22 2011 Orion Poplawski <orion@cora.nwra.com> - 3.8-0.2.beta3
- Update to 3.8-beta3
- Add commons-codec to the build jar repository

* Wed Apr 20 2011 Orion Poplawski <orion@cora.nwra.com> - 3.8-0.1.beta2
- Update to 3.8-beta2
- Add BR fontconfig needed for tests to find fonts
- Fix javadoc link

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 21 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-4
- No java >= 1:1.6.0 on ppc64

* Tue Dec 21 2010 Alexander Kurtakov <akurtako@redhat.com> 3.7-3
- No poi-contrib.jar.

* Tue Dec 21 2010 Alexander Kurtakov <akurtako@redhat.com> 3.7-2
- Url encode the source.

* Mon Dec 6 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-1
- Update to 3.7 final

* Mon Nov 8 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-0.5.beta3
- Add pom

* Mon Nov 1 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-0.4.beta3
- Fix manual package

* Wed Oct 27 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-0.3.beta3
- Update to 3.7 beta3
- Add more Requires

* Wed Sep 1 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-0.2.beta2
- Update to 3.7 beta2

* Fri Jun 25 2010 Orion Poplawski <orion@cora.nwra.com> - 3.7-0.1.beta1
- Update to 3.7 beta1
- Rebase compile-xsds patch

* Fri Jun 25 2010 Orion Poplawski <orion@cora.nwra.com> - 3.6-1
- Initial Fedora package
