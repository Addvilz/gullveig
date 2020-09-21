import logging
from enum import Enum
from typing import List

from gullveig.agent.lib.nativedp import has_python_library

LOGGER = logging.getLogger('gullveig-agent')

if has_python_library('apt'):
    import apt

if has_python_library('dnf'):
    import dnf


class PackageOrigin(Enum):
    DNF = 'DNF',
    APT = 'APT',


class Package:
    def __init__(
            self,
            pkg_origin: PackageOrigin,
            pkg_name: str,
            pkg_version: str,
            pkg_origin_ref: str = None,
            pkg_latest: str = None,
            pkg_summary: str = None,
            pkg_license: str = None,
            pkg_url: str = None
    ) -> None:
        self.origin = pkg_origin
        self.origin_ref = pkg_origin_ref
        self.name = pkg_name
        self.version = pkg_version
        self.latest = pkg_latest
        self.summary = pkg_summary
        self.license = pkg_license
        self.url = pkg_url


class PackageManager:
    def list_packages(self, limit_upgradable=False) -> List[Package]:
        raise RuntimeError('Not implemented')


class DNFPackageManager(PackageManager):
    def __init__(self) -> None:
        self.dnf_base = dnf.Base()

    @staticmethod
    def supports() -> bool:
        return has_python_library('dnf')

    def list_packages(self, limit_upgradable=False) -> List[Package]:
        packages = []
        self.dnf_base.read_comps()
        self.dnf_base.read_all_repos()
        self.dnf_base.update_cache()
        self.dnf_base.fill_sack()

        i_query = self.dnf_base.sack.query().installed()
        u_query = self.dnf_base.sack.query().upgrades()

        for pkg in i_query:
            upgrade_to_version = None
            self_upgrade_query = u_query.filter(name=pkg.name)
            upgrade_candidates = list(self_upgrade_query)

            if len(upgrade_candidates) > 0:
                upgrade_to_version = upgrade_candidates[0].evr

            if limit_upgradable and upgrade_to_version is None:
                continue

            packages.append(Package(
                pkg_origin=PackageOrigin.DNF,
                pkg_name=pkg.name,
                pkg_version=pkg.evr,
                pkg_origin_ref=pkg.reponame,
                pkg_latest=upgrade_to_version,
                pkg_summary=str(pkg.summary).replace('\n', ' ').replace('  ', ' '),
                pkg_license=pkg.license,
                pkg_url=pkg.url,
            ))

        return packages


class APTPackageManager(PackageManager):
    @staticmethod
    def supports() -> bool:
        return has_python_library('apt')

    def list_packages(self, limit_upgradable=False) -> List[Package]:
        packages = []

        # noinspection PyUnresolvedReferences
        for pkg in apt.cache.Cache():
            if not pkg.is_installed:
                continue

            installed = pkg.installed
            upgrade_to_version = None

            if pkg.is_upgradable:
                upgrade_to_version = pkg.candidate.version

            if limit_upgradable and upgrade_to_version is None:
                continue

            list_origins = pkg.installed.origins
            if pkg.is_upgradable:
                list_origins = pkg.candidate.origins

            origins = set()
            for origin in list_origins:
                if origin.component == 'now':
                    continue

                origins.add(('%s (%s)' % (origin.origin, origin.site)).strip())

            if len(origins) == 0:
                origins.add('Unknown')

            packages.append(Package(
                pkg_origin=PackageOrigin.APT,
                pkg_name=pkg.name,
                pkg_version=installed.version,
                pkg_origin_ref=', '.join(origins),
                pkg_latest=upgrade_to_version,
                pkg_summary=str(installed.summary).replace('\n', ' ').replace('  ', ' '),
                pkg_license=None,
                pkg_url=installed.homepage,
            ))

        return packages


class CompositePackageManager(PackageManager):
    def __init__(self, managers: List[PackageManager]) -> None:
        self.managers = managers

    def list_packages(self, limit_upgradable=False) -> List[Package]:
        packages = []

        for manager in self.managers:
            packages.extend(manager.list_packages(limit_upgradable))

        return packages

    @classmethod
    def instance(cls):
        if not hasattr(cls, 'rt_instance'):
            __package_managers: List[PackageManager] = []

            if DNFPackageManager.supports():
                LOGGER.debug('Found supported package manager - DNF')
                __package_managers.append(DNFPackageManager())

            if APTPackageManager.supports():
                LOGGER.debug('Found supported package manager - APT')
                __package_managers.append(APTPackageManager())

            cls.rt_instance = CompositePackageManager(__package_managers)

        return cls.rt_instance


def get_package_manager() -> PackageManager:
    return CompositePackageManager.instance()
