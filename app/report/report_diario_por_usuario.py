from ..core.redmine_ticket_report import RedmineTicketReport


class ReportDiarioPorUsuario(RedmineTicketReport):
    def __init__(self):
        self.subject = "Relatório de Tickets - Diário Por Usuário"
        self.query = """ 
            select
                to_char(j.created_on::date, 'dd/mm/yyyy') as data,
                u.firstname||' '||u.lastname as usuario,
                count(distinct j.journalized_id) as qtd,
                round(count(distinct j.journalized_id) / sum(count(distinct j.journalized_id)) over () * 100, 2)||'%' as "%",
                array_to_string(array_agg(distinct i.id::varchar), ' ') as tickets
            from users as u
            inner join journals as j on j.user_id = u.id
            inner join issues as i on i.id = j.journalized_id
            inner join projects as p on p.id = i.project_id
            inner join members as m on m.project_id = p.id and m.user_id = u.id
            where
                (j.created_on::date) = (current_date)
                and (p.name ilike '%sitac%' or p.name ilike '%sinceti%')
                and exists (
                        select 1 from member_roles as mr
                        inner join roles as r on r.id = mr.role_id
                        where 
                                mr.member_id = m.id
                                and r.name ilike '%tecnotech%'
                )
            group by j.created_on::date, usuario
            order by j.created_on::date desc, qtd desc
        """

        super().__init__()
