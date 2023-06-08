import glob
import os
from typing import List

import pandas as pd

from hipscat.catalog.catalog import CatalogType
from hipscat.catalog.dataset.dataset import Dataset
from hipscat.inspection.almanac_catalog_info import AlmanacCatalogInfo


class Almanac:
    """Single instance of an almanac, and available catalogs within namespaces"""

    def __init__(self, include_default_dir=True, dirs=None):
        """Create new almanac"""
        self.files = {}
        self.entries = {}
        self.dir_to_catalog_name = {}
        self._init_files(include_default_dir=include_default_dir, dirs=dirs)
        self._init_catalog_objects()
        self._init_catalog_links()

    def _init_files(self, include_default_dir=True, dirs=None):
        if include_default_dir:
            default_dir = AlmanacCatalogInfo.get_default_dir()
            if default_dir:
                self._add_files_to_namespace(default_dir)
        if pd.api.types.is_dict_like(dirs):
            for key, value in dirs.items():
                self._add_files_to_namespace(value, key)
        elif pd.api.types.is_list_like(dirs):
            self._add_files_to_namespace(dirs)
        elif dirs is not None:
            self._add_files_to_namespace(dirs)

    def _add_files_to_namespace(self, directory, namespace=""):
        """Get yaml files within a directory or list of directories."""
        if not pd.api.types.is_list_like(directory):
            directory = [directory]

        files = []
        for input_path in directory:
            if os.path.isfile(input_path):
                files.append(input_path)
                continue

            input_paths = glob.glob(f"{input_path}/**.yml")
            input_paths.sort()
            files.extend(input_paths)

        if namespace in self.files:
            self.files[namespace].extend(files)
        else:
            self.files[namespace] = files

    def _init_catalog_objects(self):
        for namespace, files in self.files.items():
            for file in files:
                catalog_info = AlmanacCatalogInfo.from_file(file)
                catalog_info.namespace = namespace
                if namespace:
                    full_name = f"{namespace}:{catalog_info.catalog_name}"
                else:
                    full_name = catalog_info.catalog_name
                if full_name in self.entries:
                    raise ValueError(
                        f"Duplicate catalog name ({full_name}). Try using namespaces."
                    )
                self.entries[full_name] = catalog_info
                self.dir_to_catalog_name[catalog_info.catalog_path] = full_name

    def _init_catalog_links(self):
        for catalog_entry in self.entries.values():
            if catalog_entry.catalog_type == CatalogType.OBJECT:
                pass
            elif catalog_entry.catalog_type == CatalogType.SOURCE:
                catalog_entry.primary_link = self._get_linked_catalog(
                    catalog_entry.get_primary_text(),
                    "primary",
                    "source",
                    catalog_entry.catalog_name,
                    catalog_entry.namespace,
                )
                if catalog_entry.primary_link:
                    catalog_entry.objects.append(catalog_entry.primary_link)
                    catalog_entry.primary_link.sources.append(catalog_entry)
            elif catalog_entry.catalog_type == CatalogType.ASSOCIATION:
                catalog_entry.primary_link = self._get_linked_catalog(
                    catalog_entry.get_primary_text(),
                    "primary",
                    "association",
                    catalog_entry.catalog_name,
                    catalog_entry.namespace,
                )
                catalog_entry.primary_link.associations.append(catalog_entry)
                catalog_entry.join_link = self._get_linked_catalog(
                    catalog_entry.get_join_text(),
                    "join",
                    "association",
                    catalog_entry.catalog_name,
                    catalog_entry.namespace,
                )
                catalog_entry.join_link.associations_right.append(catalog_entry)
            elif catalog_entry.catalog_type == CatalogType.MARGIN:
                catalog_entry.primary_link = self._get_linked_catalog(
                    catalog_entry.get_primary_text(),
                    "primary",
                    "margin",
                    catalog_entry.catalog_name,
                    catalog_entry.namespace,
                )
                if catalog_entry.primary_link:
                    catalog_entry.primary_link.margins.append(catalog_entry)
            elif catalog_entry.catalog_type == CatalogType.INDEX:
                catalog_entry.primary_link = self._get_linked_catalog(
                    catalog_entry.get_primary_text(),
                    "primary",
                    "index",
                    catalog_entry.catalog_name,
                    catalog_entry.namespace,
                )
                if catalog_entry.primary_link:
                    catalog_entry.primary_link.indexes.append(catalog_entry)
            else:  # pragma: no cover
                raise ValueError(f"Unknown catalog type {catalog_entry.catalog_type}")

    def _get_linked_catalog(
        self, linked_text, node_type, link_type, catalog_name, namespace
    ):
        """Find a catalog, either by original path, expanded path, raw name, or namespaced-name.

        Raises:
            ValueError: if catalog is not found in almanac
        """
        if not linked_text:
            return None
        resolved_path = os.path.expandvars(linked_text)
        if linked_text in self.dir_to_catalog_name:
            linked_text = self.dir_to_catalog_name[linked_text]
        elif resolved_path in self.dir_to_catalog_name:
            linked_text = self.dir_to_catalog_name[resolved_path]

        resolved_name = linked_text
        if not resolved_name in self.entries:
            resolved_name = f"{namespace}:{linked_text}"
            if not resolved_name in self.entries:
                raise ValueError(
                    f"{link_type} {catalog_name} missing {node_type} catalog {linked_text}"
                )
        return self.entries[resolved_name]

    def catalogs(self, include_deprecated=False, types: List[str] = None):
        """Get names of catalogs in the almanac, matching the provided conditions."""
        selected = []
        for full_name, catalog_info in self.entries.items():
            include = True
            if not include_deprecated and catalog_info.deprecated:
                include = False
            if types and catalog_info.catalog_type not in types:
                include = False

            if include:
                selected.append(full_name)
        return selected

    def get_almanac_info(self, catalog_name: str) -> AlmanacCatalogInfo:
        """Fetch the almanac info for a single catalog."""
        return self.entries[catalog_name]

    def get_catalog(self, catalog_name: str) -> Dataset:
        """Fetch the fully-populated hipscat metadata for the catalog name."""
        return Dataset.read_from_hipscat(
            self.get_almanac_info(catalog_name=catalog_name).catalog_path
        )
