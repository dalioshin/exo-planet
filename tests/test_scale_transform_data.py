import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

# Import the module to test
from exo_planet.scale_transform_data import (
    linear_scale,
    convert_to_cart,
    convert_scale_clean_df,
    generate_from_local_csv,
    generate_from_api,
    SCALE_FACTOR_CONST
)


class TestLinearScale:
    """Test suite for the linear_scale function."""
    
    def test_linear_scale_basic(self):
        """Test basic linear scaling functionality."""
        df = pd.DataFrame({'value': [0, 50, 100]})
        result = linear_scale(df, 'value', scaler=1)
        
        expected = pd.DataFrame({'value': [0.0, 0.5, 1.0]})
        pd.testing.assert_frame_equal(result, expected)
    
    def test_linear_scale_with_custom_scaler(self):
        """Test linear scaling with custom scaler value."""
        df = pd.DataFrame({'value': [10, 20, 30]})
        result = linear_scale(df, 'value', scaler=100)
        
        assert result['value'].min() == 0.0
        assert result['value'].max() == 100.0
        assert result['value'].iloc[1] == 50.0
    
    def test_linear_scale_single_value(self):
        """Test linear scaling with single unique value (edge case)."""
        df = pd.DataFrame({'value': [5, 5, 5]})
        result = linear_scale(df, 'value', scaler=1)
        
        # When min == max, division by zero results in NaN
        assert result['value'].isna().all()
    
    def test_linear_scale_negative_values(self):
        """Test linear scaling with negative values."""
        df = pd.DataFrame({'value': [-10, 0, 10]})
        result = linear_scale(df, 'value', scaler=20)
        
        assert result['value'].min() == 0.0
        assert result['value'].max() == 20.0
        assert result['value'].iloc[1] == 10.0
    
    def test_linear_scale_does_not_modify_original(self):
        """Test that linear_scale does not modify the original DataFrame."""
        df = pd.DataFrame({'value': [1, 2, 3]})
        original_values = df['value'].copy()
        
        linear_scale(df, 'value', scaler=10)
        
        pd.testing.assert_series_equal(df['value'], original_values)
    
    def test_linear_scale_preserves_other_columns(self):
        """Test that other columns are preserved during scaling."""
        df = pd.DataFrame({'value': [0, 50, 100], 'other': ['a', 'b', 'c']})
        result = linear_scale(df, 'value', scaler=1)
        
        assert 'other' in result.columns
        assert result['other'].tolist() == ['a', 'b', 'c']


class TestConvertToCart:
    """Test suite for the convert_to_cart function."""
    
    def test_convert_to_cart_basic(self):
        """Test basic conversion from polar to cartesian coordinates."""
        df = pd.DataFrame({
            'ra': [0.0],
            'dec': [0.0],
            'sy_dist': [1.0]
        })
        result = convert_to_cart(df)
        
        assert 'x' in result.columns
        assert 'y' in result.columns
        assert 'z' in result.columns
        
        # At ra=0, dec=0, sy_dist=1: x=1, y=0, z=0
        np.testing.assert_almost_equal(result['x'].iloc[0], 1.0, decimal=5)
        np.testing.assert_almost_equal(result['y'].iloc[0], 0.0, decimal=5)
        np.testing.assert_almost_equal(result['z'].iloc[0], 0.0, decimal=5)
    
    def test_convert_to_cart_90_degree_dec(self):
        """Test conversion with 90 degree declination."""
        df = pd.DataFrame({
            'ra': [0.0],
            'dec': [90.0],
            'sy_dist': [1.0]
        })
        result = convert_to_cart(df)
        
        # At dec=90, z should be ~1, x and y should be ~0
        np.testing.assert_almost_equal(result['z'].iloc[0], 1.0, decimal=5)
        np.testing.assert_almost_equal(result['x'].iloc[0], 0.0, decimal=5)
        np.testing.assert_almost_equal(result['y'].iloc[0], 0.0, decimal=5)
    
    def test_convert_to_cart_90_degree_ra(self):
        """Test conversion with 90 degree right ascension."""
        df = pd.DataFrame({
            'ra': [90.0],
            'dec': [0.0],
            'sy_dist': [1.0]
        })
        result = convert_to_cart(df)
        
        # At ra=90, dec=0: x~0, y~1, z~0
        np.testing.assert_almost_equal(result['x'].iloc[0], 0.0, decimal=5)
        np.testing.assert_almost_equal(result['y'].iloc[0], 1.0, decimal=5)
        np.testing.assert_almost_equal(result['z'].iloc[0], 0.0, decimal=5)
    
    def test_convert_to_cart_multiple_rows(self):
        """Test conversion with multiple rows."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0, 180.0],
            'dec': [0.0, 0.0, 0.0],
            'sy_dist': [1.0, 1.0, 1.0]
        })
        result = convert_to_cart(df)
        
        assert len(result) == 3
        assert all(col in result.columns for col in ['x', 'y', 'z'])
    
    def test_convert_to_cart_does_not_modify_original(self):
        """Test that convert_to_cart does not modify the original DataFrame."""
        df = pd.DataFrame({
            'ra': [45.0],
            'dec': [30.0],
            'sy_dist': [10.0]
        })
        original_columns = df.columns.tolist()
        
        convert_to_cart(df)
        
        assert df.columns.tolist() == original_columns
    
    def test_convert_to_cart_distance_scaling(self):
        """Test that distance is properly scaled in conversion."""
        df = pd.DataFrame({
            'ra': [0.0],
            'dec': [0.0],
            'sy_dist': [10.0]
        })
        result = convert_to_cart(df)
        
        # Distance should scale proportionally
        np.testing.assert_almost_equal(result['x'].iloc[0], 10.0, decimal=5)


class TestConvertScaleCleanDf:
    """Test suite for the convert_scale_clean_df function."""
    
    def test_convert_scale_clean_df_basic(self):
        """Test basic functionality of convert_scale_clean_df."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, 10.0],
            'st_teff': [5000, 6000],
            'extra_col': ['a', 'b']
        })
        
        result = convert_scale_clean_df(df)
        
        # Check that cartesian coordinates are added
        assert all(col in result.columns for col in ['x', 'y', 'z'])
        
        # Check that extra column is not in result
        assert 'extra_col' not in result.columns
        
        # Check that required columns are present
        assert all(col in result.columns for col in ['ra', 'dec', 'sy_dist', 'pl_rade', 'st_rad', 'st_teff'])
    
    def test_convert_scale_clean_df_removes_na(self):
        """Test that NaN values are removed."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0, np.nan],
            'dec': [0.0, 0.0, 45.0],
            'sy_dist': [10.0, 20.0, 30.0],
            'pl_rade': [1.0, 2.0, 3.0],
            'st_rad': [1.0, 10.0, 5.0],
            'st_teff': [5000, 6000, 5500]
        })
        
        result = convert_scale_clean_df(df)
        
        # Should have 2 rows (one with NaN removed)
        assert len(result) == 2
    
    def test_convert_scale_clean_df_removes_duplicates(self):
        """Test that duplicate sy_dist values are removed."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0, 180.0],
            'dec': [0.0, 0.0, 0.0],
            'sy_dist': [10.0, 10.0, 20.0],  # Two duplicates
            'pl_rade': [1.0, 2.0, 3.0],
            'st_rad': [1.0, 10.0, 5.0],
            'st_teff': [5000, 6000, 5500]
        })
        
        result = convert_scale_clean_df(df)
        
        # Should have 2 rows (one duplicate removed)
        assert len(result) == 2
        assert result['sy_dist'].nunique() == 2
    
    def test_convert_scale_clean_df_log_transform_radius(self):
        """Test that stellar radius is log-transformed."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, np.e],  # e^1 = e
            'st_teff': [5000, 6000]
        })
        
        result = convert_scale_clean_df(df)
        
        # log(1) = 0, log(e) = 1
        assert result['st_rad'].min() >= 0
    
    def test_convert_scale_clean_df_scales_distance(self):
        """Test that sy_dist is scaled by SCALE_FACTOR_CONST."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, 10.0],
            'st_teff': [5000, 6000]
        })
        
        result = convert_scale_clean_df(df)
        
        # After scaling, max should be SCALE_FACTOR_CONST
        assert result['sy_dist'].max() == SCALE_FACTOR_CONST
        assert result['sy_dist'].min() == 0.0
    
    def test_convert_scale_clean_df_scales_stellar_radius(self):
        """Test that st_rad is scaled to max of 3."""
        df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, 100.0],
            'st_teff': [5000, 6000]
        })
        
        result = convert_scale_clean_df(df)
        
        # After log and scaling, max should be 3
        assert result['st_rad'].max() == 3.0
        assert result['st_rad'].min() == 0.0


class TestGenerateFromLocalCsv:
    """Test suite for the generate_from_local_csv function."""
    
    @patch('exo_planet.scale_transform_data.save_to_csv')
    @patch('exo_planet.scale_transform_data.load_from_csv')
    def test_generate_from_local_csv_basic(self, mock_load, mock_save):
        """Test basic functionality of generate_from_local_csv."""
        # Setup mock data
        mock_df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, 10.0],
            'st_teff': [5000, 6000]
        })
        mock_load.return_value = mock_df
        
        # Call function
        generate_from_local_csv('input.csv', 'output.csv')
        
        # Verify load_from_csv was called with correct argument
        mock_load.assert_called_once_with('input.csv')
        
        # Verify save_to_csv was called
        mock_save.assert_called_once()
        
        # Verify the DataFrame passed to save has the correct columns
        saved_df = mock_save.call_args[0][0]
        assert all(col in saved_df.columns for col in ['x', 'y', 'z'])
        
        # Verify output filename
        assert mock_save.call_args[0][1] == 'output.csv'
    
    @patch('exo_planet.scale_transform_data.save_to_csv')
    @patch('exo_planet.scale_transform_data.load_from_csv')
    def test_generate_from_local_csv_data_flow(self, mock_load, mock_save):
        """Test that data flows correctly through the pipeline."""
        mock_df = pd.DataFrame({
            'ra': [0.0],
            'dec': [0.0],
            'sy_dist': [10.0],
            'pl_rade': [1.0],
            'st_rad': [1.0],
            'st_teff': [5000]
        })
        mock_load.return_value = mock_df
        
        generate_from_local_csv('test_input.csv', 'test_output.csv')
        
        # Verify data was transformed
        saved_df = mock_save.call_args[0][0]
        assert len(saved_df) == 1
        assert 'x' in saved_df.columns


class TestGenerateFromApi:
    """Test suite for the generate_from_api function."""
    
    @patch('exo_planet.scale_transform_data.save_to_csv')
    @patch('exo_planet.scale_transform_data.pull_from_astro_api')
    def test_generate_from_api_basic(self, mock_pull, mock_save):
        """Test basic functionality of generate_from_api."""
        # Setup mock data
        mock_df = pd.DataFrame({
            'ra': [0.0, 90.0],
            'dec': [0.0, 0.0],
            'sy_dist': [10.0, 20.0],
            'pl_rade': [1.0, 2.0],
            'st_rad': [1.0, 10.0],
            'st_teff': [5000, 6000]
        })
        mock_pull.return_value = mock_df
        
        # Call function
        generate_from_api('output.csv')
        
        # Verify pull_from_astro_api was called with correct arguments
        mock_pull.assert_called_once_with(
            'ps',
            ["ra", "dec", "sy_dist", "pl_rade", "st_rad", "st_teff"]
        )
        
        # Verify save_to_csv was called
        mock_save.assert_called_once()
        
        # Verify output filename
        assert mock_save.call_args[0][1] == 'output.csv'
    
    @patch('exo_planet.scale_transform_data.save_to_csv')
    @patch('exo_planet.scale_transform_data.pull_from_astro_api')
    def test_generate_from_api_correct_columns(self, mock_pull, mock_save):
        """Test that correct columns are requested from API."""
        mock_df = pd.DataFrame({
            'ra': [0.0],
            'dec': [0.0],
            'sy_dist': [10.0],
            'pl_rade': [1.0],
            'st_rad': [1.0],
            'st_teff': [5000]
        })
        mock_pull.return_value = mock_df
        
        generate_from_api('test_output.csv')
        
        # Check that the correct column list was passed
        call_args = mock_pull.call_args[0]
        expected_columns = ["ra", "dec", "sy_dist", "pl_rade", "st_rad", "st_teff"]
        assert call_args[1] == expected_columns
    
    @patch('exo_planet.scale_transform_data.save_to_csv')
    @patch('exo_planet.scale_transform_data.pull_from_astro_api')
    def test_generate_from_api_data_transformation(self, mock_pull, mock_save):
        """Test that data is properly transformed before saving."""
        mock_df = pd.DataFrame({
            'ra': [45.0],
            'dec': [30.0],
            'sy_dist': [15.0],
            'pl_rade': [1.5],
            'st_rad': [2.0],
            'st_teff': [5500]
        })
        mock_pull.return_value = mock_df
        
        generate_from_api('output.csv')
        
        # Verify the saved DataFrame has cartesian coordinates
        saved_df = mock_save.call_args[0][0]
        assert all(col in saved_df.columns for col in ['x', 'y', 'z'])
        assert len(saved_df) == 1


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def test_convert_scale_clean_df_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame(columns=['ra', 'dec', 'sy_dist', 'pl_rade', 'st_rad', 'st_teff'])
        
        result = convert_scale_clean_df(df)
        
        assert len(result) == 0
    
    def test_convert_scale_clean_df_all_na(self):
        """Test handling of DataFrame with all NaN values."""
        df = pd.DataFrame({
            'ra': [np.nan, np.nan],
            'dec': [np.nan, np.nan],
            'sy_dist': [np.nan, np.nan],
            'pl_rade': [np.nan, np.nan],
            'st_rad': [np.nan, np.nan],
            'st_teff': [np.nan, np.nan]
        })
        
        result = convert_scale_clean_df(df)
        
        assert len(result) == 0
    
    def test_linear_scale_with_zero_scaler(self):
        """Test linear scaling with zero scaler."""
        df = pd.DataFrame({'value': [0, 50, 100]})
        result = linear_scale(df, 'value', scaler=0)
        
        assert result['value'].max() == 0.0
        assert result['value'].min() == 0.0


# Fixture for common test data
@pytest.fixture
def sample_exoplanet_data():
    """Fixture providing sample exoplanet data for tests."""
    return pd.DataFrame({
        'ra': [0.0, 45.0, 90.0, 135.0, 180.0],
        'dec': [0.0, 30.0, -30.0, 60.0, -60.0],
        'sy_dist': [10.0, 20.0, 30.0, 40.0, 50.0],
        'pl_rade': [1.0, 1.5, 2.0, 0.5, 3.0],
        'st_rad': [1.0, 2.0, 5.0, 10.0, 50.0],
        'st_teff': [5000, 5500, 6000, 4500, 7000]
    })


class TestIntegration:
    """Integration tests for the full pipeline."""
    
    def test_full_pipeline_local(self, sample_exoplanet_data, tmp_path):
        """Test the complete pipeline from loading to saving."""
        # Create temporary CSV files
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"
        
        # Save sample data
        sample_exoplanet_data.to_csv(input_file, index=False)
        
        # Mock the data_func functions
        with patch('exo_planet.scale_transform_data.load_from_csv', return_value=sample_exoplanet_data):
            with patch('exo_planet.scale_transform_data.save_to_csv') as mock_save:
                generate_from_local_csv(str(input_file), str(output_file))
                
                # Verify save was called
                assert mock_save.called
                
                # Verify output has correct structure
                saved_df = mock_save.call_args[0][0]
                assert 'x' in saved_df.columns
                assert 'y' in saved_df.columns
                assert 'z' in saved_df.columns
                assert len(saved_df) <= len(sample_exoplanet_data)