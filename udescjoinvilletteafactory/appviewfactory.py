from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMainWindow

from udescjoinvilletteaview import (AboutView, CalibrationView,
                                    ProfessionalEditView,
                                    ProfessionalListView,
                                    InstitutionFacilityEditView,
                                    InstitutionFacilityListView, LanguageView,
                                    MainView, PlayerEditView,
                                    PlayerGameLaunchView, PlayerListView)

# Type checking to prevent circular import on run time
if TYPE_CHECKING:
    # Local module import
    from udescjoinvilletteamodel import (Professional,
                                         InstitutionFacility, Player)


class AppViewFactory:
    """A factory class for creating application view instances.
    This class provides static methods to instantiate various view classes
    used in the application, such as PlayerEditView, PlayerListView,
    AboutView, and LanguageView. It facilitates the creation of view
    objects with optional parameters for parent widgets and other
    dependencies.

    Methods
    -------
    create_player_edit_view(parent=None, player=None)
        Create an instance of PlayerEditView.
    create_player_list_view(parent=None, player_edit_view=None)
        Create an instance of PlayerListView.
    create_about_view(parent=None)
        Create an instance of AboutView.
    create_language_view(translator=None, parent=None)
        Create an instance of LanguageView.

    """

    @staticmethod
    def create_player_edit_view(
        parent: Optional[QDialog] = None, player: Optional["Player"] = None
    ) -> PlayerEditView:
        """
        Create an instance of PlayerEditView.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            The parent dialog for the PlayerEditView, by default None.
        player : Optional[Player], optional
            The player object to be edited, by default None.

        Returns
        -------
        PlayerEditView
            An instance of PlayerEditView configured with the provided
            parent and player.
        """
        return PlayerEditView(parent, player)

    @staticmethod
    def create_player_list_view(
        parent: Optional[QObject] = None,
        player_edit_view: Optional[
            Callable[[Optional[QDialog], Optional["Player"]], PlayerEditView]
        ] = None,
    ) -> PlayerListView:
        """
        Create an instance of PlayerListView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the PlayerListView, by default None.
        player_edit_view : Optional[Callable], optional
            A callable to create a PlayerEditView instance, by default
            None.

        Returns
        -------
        PlayerListView
            An instance of PlayerListView configured with the provided
            parent and player_edit_view callable.
        """
        return PlayerListView(parent, player_edit_view)

    @staticmethod
    def create_professional_edit_view(
        parent: Optional[QDialog] = None,
        professional: Optional["Professional"] = None,
    ) -> ProfessionalEditView:
        """
        Create an instance of ProfessionalEditView.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            The parent dialog for the ProfessionalEditView,
            by default None.
        professional : Optional[Professional], optional
            The professional object to be edited, by default None.

        Returns
        -------
        ProfessionalEditView
            An instance of ProfessionalEditView configured
            with the provided parent and professional.
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
        return ProfessionalListView(parent, professional_edit_view)

    @staticmethod
    def create_institutionfacility_edit_view(
        parent: Optional[QDialog] = None,
        institutionfacility: Optional["InstitutionFacility"] = None,
    ) -> InstitutionFacilityEditView:
        """
        Create an instance of InstitutionFacilityEditView.

        Parameters
        ----------
        parent : Optional[QDialog], optional
            The parent dialog for the InstitutionFacilityEditView,
            by default None.
        institutionfacility : Optional[InstitutionFacility], optional
            The institutionfacility object to be edited, by default None.

        Returns
        -------
        InstitutionFacilityEditView
            An instance of InstitutionFacilityEditView configured
            with the provided parent and institutionfacility.
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

        return InstitutionFacilityListView(
            parent, institutionfacility_edit_view
        )

    @staticmethod
    def create_about_view(parent: Optional[QDialog] = None) -> AboutView:
        """
        Create an instance of AboutView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the AboutView, by default None.

        Returns
        -------
        AboutView
            An instance of AboutView configured with the provided parent.
        """
        return AboutView(parent)

    @staticmethod
    def create_calibration_view(
        parent: Optional[QDialog] = None,
    ) -> CalibrationView:
        """
        Create an instance of CalibrationView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the CalibrationView, by default None.

        Returns
        -------
        CalibrationView
            An instance of CalibrationView configured with the provided parent.
        """
        return CalibrationView(parent)

    @staticmethod
    def create_playergamelauch_view(
        parent: Optional[QDialog] = None,
    ) -> CalibrationView:
        """
        Create an instance of PlayerGameLaunchView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the PlayerGameLaunchView, by default None.

        Returns
        -------
        PlayerGameLaunchView
            An instance of PlayerGameLaunchView configured with the provided parent.
        """
        return PlayerGameLaunchView(parent)

    @staticmethod
    def create_language_view(parent: Optional[QDialog] = None) -> LanguageView:
        """
        Create an instance of LanguageView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the LanguageView, by default None.

        Returns
        -------
        LanguageView
            An instance of LanguageView configured with the provided
            translator and parent.
        """
        return LanguageView(parent)

    @staticmethod
    def create_main_view(parent: Optional[QMainWindow] = None) -> MainView:
        """
        Create an instance of MainView.

        Parameters
        ----------
        parent : Optional[QObject], optional
            The parent object for the MainView, by default None.

        Returns
        -------
        MainView
            An instance of MainView configured with the provided
            translator and parent.
        """
        return MainView(parent)
