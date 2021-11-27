import subprocess
from os.path import basename, join

import numpy as np
import pytest
from nilearn.input_data import NiftiLabelsMasker


def test_integration_pfm(testpath, bold_file, atlas_file, AUC_file, skip_integration):
    if skip_integration:
        pytest.skip("Skipping integration test")
    auc_output = join(testpath, "auc_local.nii.gz")
    subprocess.call(
        "export mode=integration_pfm && "
        "connPFM -i {} -a {} --AUC {} -tr 1 -u vferrer -job 0 -nsur 1 -w pfm".format(
            bold_file, atlas_file, auc_output
        ),
        shell=True,
    )
    masker = NiftiLabelsMasker(
        labels_img=atlas_file,
        standardize=False,
        strategy="mean",
        resampling_target=None,
    )
    # compare the AUC values
    auc_osf = masker.fit_transform(AUC_file)
    auc_local = masker.fit_transform(auc_output)
    np.all(auc_osf == auc_local)


def test_integration_ev(
    testpath, bold_file, atlas_file, AUC_file, ets_auc_denoised_file, surr_dir, skip_integration
):
    if skip_integration:
        pytest.skip("Skipping integration test")
    subprocess.call(
        "connPFM -i {} -a {} --AUC {} -d {} -m {} -tr 1 -u vferrer -nsur 50 -w ev".format(
            bold_file, atlas_file, AUC_file, surr_dir, join(testpath, "ets_AUC_denoised.txt")
        ),
        shell=True,
    )
    ets_auc_denoised_local = np.loadtxt(join(testpath, "ets_AUC_denoised.txt"))
    ets_auc_osf = np.loadtxt(join(ets_auc_denoised_file))
    np.all(ets_auc_denoised_local == ets_auc_osf)


def test_integration_debias(
    testpath,
    bold_file,
    atlas_file,
    AUC_file,
    ets_auc_denoised_file,
    surr_dir,
    beta_file,
    fitt_file,
    skip_integration,
):
    if skip_integration:
        pytest.skip("Skipping integration test")
    subprocess.call(
        "connPFM -i {} -a {} --AUC {} -d {} -m {} -tr 1 -u vferrer -nsur 50 -w debias".format(
            bold_file, atlas_file, AUC_file, surr_dir, ets_auc_denoised_file
        ),
        shell=True,
    )
    masker = NiftiLabelsMasker(
        labels_img=atlas_file,
        standardize=False,
        strategy="mean",
    )
    beta_osf = masker.fit_transform(beta_file)
    fitt_osf = masker.fit_transform(fitt_file)
    beta_local = masker.fit_transform(
        join(testpath, f"{basename(bold_file[:-7])}_beta_ETS.nii.gz")
    )
    fitt_local = masker.fit_transform(
        join(testpath, f"{basename(bold_file[:-7])}_fitt_ETS.nii.gz")
    )
    np.all(beta_osf == beta_local)
    np.all(fitt_osf == fitt_local)
