"""Factory helpers for creating application views.

This module provides the AppViewFactory class, which centralizes the
creation of application views used across the T-TEA platform.
"""

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMainWindow

from ttea.view import (AboutView, AutomaticCalibrationView,
                       CalibrationSettingView, CalibrationView,
                       InstitutionFacilityEditView,
                       InstitutionFacilityListView, LanguageView, MainView,
                       ManualCalibrationView, PlayerEditView,
                       PlayerGameLaunchView, PlayerListView,
                       ProfessionalEditView, ProfessionalListView)

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    from ttea.model import InstitutionFacility, Player, Professional


class AppViewFactory:
    """Factory for application view instances.

    This class provides static methods to instantiate the views used in
    the application. It centralizes view construction so callers do not
    need to import view classes directly.

    Methods
    -------
    create_player_edit_view(parent=None, player=None)
        Create a new ``PlayerEditView``.
    create_player_list_view(parent=None, player_edit_view=None)
        Create a new ``PlayerListView``.
    create_professional_edit_view(parent=None, professional=None)
        Create a new ``ProfessionalEditView``.
    create_professional_list_view(parent=None, ...)
        Create a new ``ProfessionalListView``.
    create_institutionfacility_edit_view(parent=None, ...)
        Create a new ``InstitutionFacilityEditView``.
    create_institutionfacility_list_view(parent=None, ...)
        Create a new ``InstitutionFacilityListView``.
    create_about_view(parent=None)
        Create a new ``AboutView``.
    create_calibration_view(parent=None)
        Create a new ``CalibrationView``.
    create_playergamelauch_view(parent=None)
        Create a new ``PlayerGameLaunchView``.
    create_language_view(parent=None)
        Create a new ``LanguageView``.
    create_main_view(parent=None)
        Create a new ``MainView``.
    create_manualcalibration_view(parent=None)
        Create a new ``ManualCalibrationView``.
    create_automaticcalibration_view(parent=None)
        Create a new ``AutomaticCalibrationView``.
    create_calibrationsetting_view(parent=None)
        Create a new ``CalibrationSettingView``.
    """

    @staticmethod
    def create_player_edit_view(
        parent: Optional[QDialog] = None, player: Optional["Player"] = None
    ) -> PlayerEditView:
        """Create a new ``PlayerEditView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.
        player : Player | None, optional
            Player to edit; None creates a new player. Default is None.

        Returns
        -------
        PlayerEditView
            The new view.
        """
        return PlayerEditView(parent, player)

    @staticmethod
    def create_player_list_view(
        parent: Optional[QObject] = None,
        player_edit_view: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], PlayerEditView]
        ] = None,
    ) -> PlayerListView:
        """Create a new ``PlayerListView``.

        Parameters
        ----------
        parent : QObject | None, optional
            Parent of the view. Default is None.
        player_edit_view : Callable | None, optional
            Callable ``(parent, player) -> PlayerEditView`` used to open
            the edit view. Default is None.

        Returns
        -------
        PlayerListView
            The new view.
        """
        return PlayerListView(parent, player_edit_view)

    @staticmethod
    def create_professional_edit_view(
        parent: Optional[QDialog] = None,
        professional: Optional["Professional"] = None,
    ) -> ProfessionalEditView:
        """Create a new ``ProfessionalEditView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.
        professional : Professional | None, optional
            Professional to edit; None creates a new one. Default is
            None.

        Returns
        -------
        ProfessionalEditView
            The new view.
        """
        return ProfessionalEditView(parent, professional)

    @staticmethod
    def create_professional_list_view(
        parent: Optional[QObject] = None,
        professional_edit_view: Optional[
            Callable[
                [Optional[QDialog], Optional["Professional"]],
                ProfessionalEditView,
            ]
        ] = None,
    ) -> ProfessionalListView:
        """Create a new ``ProfessionalListView``.

        Parameters
        ----------
        parent : QObject | None, optional
            Parent of the view. Default is None.
        professional_edit_view : Callable | None, optional
            Callable ``(parent, professional) -> ProfessionalEditView``
            used to open the edit view. Default is None.

        Returns
        -------
        ProfessionalListView
            The new view.
        """
        return ProfessionalListView(parent, professional_edit_view)

    @staticmethod
    def create_institutionfacility_edit_view(
        parent: Optional[QDialog] = None,
        institutionfacility: Optional["InstitutionFacility"] = None,
    ) -> InstitutionFacilityEditView:
        """Create a new ``InstitutionFacilityEditView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.
        institutionfacility : InstitutionFacility | None, optional
            Facility to edit; None creates a new one. Default is None.

        Returns
        -------
        InstitutionFacilityEditView
            The new view.
        """
        return InstitutionFacilityEditView(parent, institutionfacility)

    @staticmethod
    def create_institutionfacility_list_view(
        parent: Optional[QObject] = None,
        institutionfacility_edit_view: Optional[
            Callable[
                [Optional[QDialog], Optional["InstitutionFacility"]],
                InstitutionFacilityEditView,
            ]
        ] = None,
    ) -> InstitutionFacilityListView:
        """Create a new ``InstitutionFacilityListView``.

        Parameters
        ----------
        parent : QObject | None, optional
            Parent of the view. Default is None.
        institutionfacility_edit_view : Callable | None, optional
            Callable that creates the edit view from ``(parent,
            institutionfacility)``. Default is None.

        Returns
        -------
        InstitutionFacilityListView
            The new view.
        """
        return InstitutionFacilityListView(
            parent, institutionfacility_edit_view
        )

    @staticmethod
    def create_about_view(parent: Optional[QDialog] = None) -> AboutView:
        """Create a new ``AboutView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        AboutView
            The new view.
        """
        return AboutView(parent)

    @staticmethod
    def create_calibration_view(
        parent: Optional[QDialog] = None,
    ) -> CalibrationView:
        """Create a new ``CalibrationView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        CalibrationView
            The new view.
        """
        return CalibrationView(parent)

    @staticmethod
    def create_playergamelauch_view(
        parent: Optional[QDialog] = None,
    ) -> PlayerGameLaunchView:
        """Create a new ``PlayerGameLaunchView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        PlayerGameLaunchView
            The new view.
        """
        return PlayerGameLaunchView(parent)

    @staticmethod
    def create_language_view(parent: Optional[QDialog] = None) -> LanguageView:
        """Create a new ``LanguageView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        LanguageView
            The new view.
        """
        return LanguageView(parent)

    @staticmethod
    def create_main_view(parent: Optional[QMainWindow] = None) -> MainView:
        """Create a new ``MainView``.

        Parameters
        ----------
        parent : QMainWindow | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        MainView
            The new view.
        """
        return MainView(parent)

    @staticmethod
    def create_manualcalibration_view(
        parent: Optional[QDialog] = None,
    ) -> ManualCalibrationView:
        """Create a new ``ManualCalibrationView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        ManualCalibrationView
            The new view.
        """
        return ManualCalibrationView(parent)

    @staticmethod
    def create_automaticcalibration_view(
        parent: Optional[QDialog] = None,
    ) -> AutomaticCalibrationView:
        """Create a new ``AutomaticCalibrationView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        AutomaticCalibrationView
            The new view.
        """
        return AutomaticCalibrationView(parent)

    @staticmethod
    def create_calibrationsetting_view(
        parent: Optional[QDialog] = None,
    ) -> CalibrationSettingView:
        """Create a new ``CalibrationSettingView``.

        Parameters
        ----------
        parent : QDialog | None, optional
            Parent of the view. Default is None.

        Returns
        -------
        CalibrationSettingView
            The new view.
        """
        return CalibrationSettingView(parent)
