#!/usr/bin/env python2.5

if __name__ == '__main__':
    import virtualenv, textwrap
    output = virtualenv.create_bootstrap_script(textwrap.dedent("""
        import os, subprocess

        def extend_parser(parser):
            parser.add_option(
                '--simplsale',
                metavar = 'VERSION',
                dest = 'simplsale_version',
                default = 'latest',
                help = '"latest", "manual", or a specific version '
                       'of SimplSale to install.',
                )

        def after_install(options, home_dir):
            home_dir = os.path.abspath(home_dir)
            lib = join(home_dir, 'lib')
            # Install libxml2
            cmmi(
                home_dir = home_dir,
                name = 'libxml2',
                url = 'http://code.3purple.com/3rdparty/libxml2-2.6.30.tar.gz',
                extra_options = ['--without-python'],
                )
            # Install libxslt
            cmmi(
                home_dir = home_dir,
                name = 'libxslt',
                url = 'http://code.3purple.com/3rdparty/libxslt-1.1.22.tar.gz',
                extra_options = [
                    '--with-libxml-prefix=%s' % home_dir,
                    '--without-python',
                    ],
                )
            # Install lxml
            easy_install_custom(
                home_dir = home_dir,
                name = 'lxml',
                package = 'lxml==2.0alpha6',
                build_ext_options = [
                    '--include-dirs=%s/include' % home_dir,
                    '--rpath=%s/lib' % home_dir,
                    ],
                )
            # Install SimplSale
            simplsale_version = options.simplsale_version.lower().strip()
            if simplsale_version == 'latest':
                easy_install(home_dir, 'SimplSale')
            elif simplsale_version == 'manual':
                print 'Please now install SimplSale manually.'
            else:
                easy_install(home_dir, 'SimplSale==%s' % simplsale_version)

        def cmmi(home_dir, name, url, extra_options):
            import urllib2, tarfile
            # Create workspace to compile in.
            workspace = join(home_dir, 'src', name)
            if not os.path.exists(workspace):
                os.makedirs(workspace)
                # Extract the package to the workspace.
                print 'Extracting', url, 'to', workspace
                basename = os.path.basename(url)
                tar_gz = urllib2.urlopen(url)
                tar = tarfile.TarFile.open(
                    name = basename,
                    fileobj = tar_gz, 
                    mode = 'r|*',
                    )
                tar.extractall(workspace)
                tar.close()
                tar_gz.close()
                # Assume that the only file in the workspace is a directory,
                # and that it is the directory that we want to build within.
                src = join(workspace, os.listdir(workspace)[0])
                os.chdir(src)
                args = [
                    join(src, 'configure'),
                    '--prefix=%s' % home_dir,
                    ]
                args.extend(extra_options)
                print ' '.join(args)
                subprocess.call(args)
                print 'make'
                subprocess.call(['make'])
                print 'make install'
                subprocess.call(['make', 'install'])
            else:
                print 'Already extracted', name

        def easy_install(home_dir, package):
            subprocess.call([join(home_dir, 'bin', 'easy_install'), package])

        def easy_install_custom(home_dir, name, package, build_ext_options):
            # Create workspace to build in.
            workspace = join(home_dir, 'src', name)
            if not os.path.exists(workspace):
                os.makedirs(workspace)
                # Extract the package to the workspace.
                print 'Extracting', package, 'to', workspace
                os.chdir(workspace)
                subprocess.call([
                    join(home_dir, 'bin', 'easy_install'),
                    '-eb.',
                    package,
                    ])
                # Assume that the only file in the workspace is a directory,
                # and that it is the directory that we want to build within.
                src = join(workspace, os.listdir(workspace)[0])
                os.chdir(src)
                python= join(home_dir, 'bin', py_version)
                args = [python25, 'setup.py', 'build_ext'] + build_ext_options
                args.extend(['develop'])
                print 'Building with', ' '.join(args)
                subprocess.call(args)
            else:
                print 'Already extracted', name
        """))
    f = open('simplsale-bootstrap.py', 'w').write(output)
