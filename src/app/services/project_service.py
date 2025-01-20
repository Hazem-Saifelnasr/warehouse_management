# src/app/services/project_service.py

from datetime import datetime, UTC
from fastapi import HTTPException, Depends
from psycopg2.extensions import JSONB
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval, ApprovalStatus
from src.app.models.project import Project
from src.app.schemas.project import ProjectCreate, ProjectUpdate
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class ProjectService:
    @staticmethod
    def create_project(project: ProjectCreate, requester_id: int, db: Session = Depends(get_db)):
        # Step 1: Check for duplicate project name within the same location
        existing_project = db.query(Project).filter(Project.name == project.name,
                                                    Project.location_id == project.location_id).first()
        if existing_project:
            raise HTTPException(status_code=400,
                                detail="Project with this name already exists in the specified location")

        # Step 2: Check if a pending approval for the same name already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "project",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value["name"].astext == project.name
        ).first()

        if existing_request:
            raise HTTPException(status_code=400,
                                detail="A pending approval request for this project name already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            new_project = Project(**dict(project))
            new_project.is_approved = True
            new_project.is_active = True
            new_project.created_by = requester_id
            new_project.created_at = datetime.now(UTC)

            db.add(new_project)  # Add the project to the session
            db.commit()
            db.refresh(new_project)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "project", new_project.id, "create", requester_id)
            return new_project

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            entity_id=None,  # New project, no ID yet
            action="create",
            new_value_dict=project.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_project(project_id: int, update_data: ProjectUpdate, requester_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.is_active:
            raise HTTPException(status_code=404, detail="Project not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(project, key, value)

            db.commit()
            db.refresh(project)

            HistoryLogService.log_action(db, "project", project_id, "update", requester_id)
            return project

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            entity_id=project_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_project_soft(project_id: int, requester_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.is_active:
            raise HTTPException(status_code=404, detail="Project not found")

        if has_approval_privileges(db, requester_id):
            project.is_deleted = True
            project.is_active = False
            project.deleted_at = datetime.now(UTC)
            project.deleted_by = requester_id

            db.commit()
            db.refresh(project)
            HistoryLogService.log_action(db, "project", project_id, "soft_delete", requester_id)
            return {"detail": "Project deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            action="delete",
            entity_id=project_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_project_permanent(project_id: int, requester_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        meta_data = {"id": project.id, "name": project.name}
        if has_approval_privileges(db, requester_id):
            db.delete(project)
            db.commit()

            # Log permanent deletion
            HistoryLogService.log_action(db, "project", project_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "Project deleted permanently"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            action="delete_permanent",
            entity_id=project_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_project(project_id: int, requester_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.is_active:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.is_deleted:
            raise HTTPException(status_code=400, detail="Project is already deleted")

        if project.is_archived:
            raise HTTPException(status_code=400, detail="Project is already archived")

        if has_approval_privileges(db, requester_id):
            project.is_archived = True
            project.is_active = False
            project.archived_at = datetime.now(UTC)
            project.archived_by = requester_id

            db.commit()
            db.refresh(project)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "project", project_id, "archive", requester_id)
            return {"detail": "Project archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            action="archive",
            entity_id=project_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_project(project_id: int, requester_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            if project.is_approved:
                project.is_deleted = False
                project.is_archived = False
                project.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "project", project_id, "restore", requester_id)
            return {"detail": "Project restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="project",
            action="restore",
            entity_id=project_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_project(project_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.is_active:
            if project.is_archived:
                raise HTTPException(status_code=404, detail="Project is archived")
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def list_projects(db: Session = Depends(get_db)):
        projects = db.query(Project).filter(Project.is_active == True).all()
        return projects

    @staticmethod
    def get_projects_by_location(location_id: int, db: Session = Depends(get_db)):
        """
        Fetch all projects for a given location.
        """
        return db.query(Project).filter(Project.location_id == location_id,
                                        Project.is_active == True).all()

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates a location without approval checks.
        """
        new_value = ProjectCreate(**new_value)  # Convert dictionary to ProjectCreate model
        project = db.query(Project).filter(Project.name == new_value.name).first()
        if project:
            raise HTTPException(status_code=400, detail="Project already exist")

        new_project = Project(**dict(new_value))
        new_project.is_approved = True
        new_project.is_active = True
        new_project.created_by = new_value.created_by
        new_project.created_at = datetime.now(UTC)

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == entity_id).first()
        if not project or not project.is_active:
            raise HTTPException(status_code=404, detail="Project not found")
        for key, value in new_value.items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == entity_id).first()
        project.is_deleted = True
        project.is_active = False
        db.commit()
        db.refresh(project)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == entity_id).first()
        project.is_archived = True
        project.is_active = False

        db.commit()
        db.refresh(project)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        project = db.query(Project).filter(Project.id == entity_id).first()
        project.is_deleted = False
        project.is_archived = False
        project.is_active = True

        db.commit()
        db.refresh(project)
