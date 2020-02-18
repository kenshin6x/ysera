from ..core.redmine_ticket_report import RedmineTicketReport


class ReportDiarioPorUsuario(RedmineTicketReport):
    def __init__(self):
        self.subject = "Relatório de Tickets - Diário Por Usuário"
        self.query = """ 
            select distinct
            to_char(current_date, 'dd/mm/yyyy') as data,
            u.firstname||' '||u.lastname as usuario,
            (
                select
                    count (distinct j.journalized_id)
                from journals j
                where j.user_id = u.id
                    and (j.created_on::date) = (current_date)
            ) as qtd,
            coalesce((
                select
                    array_to_string(array_agg(distinct i.id::varchar), ' ')
                from journals j
                inner join issues as i on i.id = j.journalized_id
                where j.user_id = u.id
                    and (j.created_on::date) = (current_date)
            ), '---') as tickets
        from users u
        inner join members m on m.user_id = u.id
        inner join member_roles mr on mr.member_id = m.id 
        inner join roles r on r.id = mr.role_id
        inner join projects p on p.id = m.project_id 
        where
            r.name ilike '%tecnotech%'
            and p.status = 1 -- ativo
            and u.status = 1 -- ativo
            and u.type = 'User'
        order by qtd desc, usuario asc
        """

        super().__init__()
