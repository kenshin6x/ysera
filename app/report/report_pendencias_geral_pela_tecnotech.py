#!python
# -*- coding: utf-8 -*-

from ..core.redmine_ticket_report import RedmineTicketReport


class ReportPendenciasGeralPelaTecnotech(RedmineTicketReport):
    def __init__(self):
        self.subject = "Relatório de Tickets - Pendências - Geral Pela Tecnotech"
        self.query = """ 
            select
                upper(x.projeto) as projeto,
                x.pendentes,
                x.pendentes_desenvolvimento as "pendentes pelo desenvolvimento",
                x."% pendentes pelo desenvolvimento",
                x.pendentes_suporte as "pendentes pelo suporte",
                x."% pendentes pelo suporte"
                from (
                select
                    *,
                    case when x.total > 0 then round((x.resolvidos::numeric * 100 / x.total), 2) || '%' else '0' end as "% resolvidos",
                    case when x.pendentes > 0 then round((x.pendentes_desenvolvimento::numeric * 100 / x.pendentes), 2) || '%' else '0' end as"% pendentes pelo desenvolvimento",
                    case when x.pendentes > 0 then round((x.pendentes_suporte::numeric * 100 / x.pendentes), 2) || '%' else '0' end as "% pendentes pelo suporte"
                from (
                    select
                        x.projeto,
                        sum(x.total) as total,
                        sum(x.resolvidos) as resolvidos,
                        sum(x.pendentes) as pendentes,
                        sum(x.pendentes_desenvolvimento) as pendentes_desenvolvimento,
                        sum(x.pendentes_suporte) as pendentes_suporte
                    from (
                        select
                        case when p.name ilike '%sitac%' then 'sitac'
                             when p.name ilike 'sinceti%' then 'sinceti'
                        end as projeto,
                        (select count(distinct i.id) from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id) as total,
                        (select count(distinct i.id) from issues as i inner join issue_statuses as si on si.id = i.status_id where i.project_id = p.id and si.is_closed is true) as resolvidos,
                        (select count(distinct i.id) from issues as i
                        inner join users as u on u.id = i.assigned_to_id
                        inner join members as m on m.project_id = p.id and m.user_id = u.id
                        inner join issue_statuses as si on si.id = i.status_id
                        where
                            i.project_id = p.id
                            and si.is_closed is false
                            and exists (
                                    select 1 from member_roles as mr
                                    inner join roles as r on r.id = mr.role_id
                                    where
                                            mr.member_id = m.id
                                            and r.name ilike '%tecnotech%'
                            )
                        ) as pendentes,
                        (select count(distinct i.id) from issues as i
                        inner join users as u on u.id = i.assigned_to_id
                        inner join members as m on m.project_id = p.id and m.user_id = u.id
                        inner join issue_statuses as si on si.id = i.status_id
                        where
                            i.project_id = p.id
                            and si.is_closed is false
                            and exists (
                                    select 1 from member_roles as mr
                                    inner join roles as r on r.id = mr.role_id
                                    where
                                            mr.member_id = m.id
                                            and r.name ilike '%desenvolvimento%'
                            )
                        ) as pendentes_desenvolvimento,
                        (select count(*) from issues as i
                        left join users as u on u.id = i.assigned_to_id
                        left join members as m on m.project_id = p.id and m.user_id = u.id
                        inner join issue_statuses as si on si.id = i.status_id
                        where
                            i.project_id = p.id
                            and si.is_closed is false
                            and (exists (
                                    select 1 from member_roles as mr
                                    inner join roles as r on r.id = mr.role_id
                                    where
                                            mr.member_id = m.id
                                            and r.name ilike '%suporte%'
                            )
                            )
                        ) as pendentes_suporte
                        from projects as p
                        where
                            (p.name ilike '%sitac%' or p.name ilike '%sinceti%')
                        order by total desc, p.name asc
                    ) as x
                    group by x.projeto
                ) as x
            ) as x
            order by x.pendentes desc
        """

        super().__init__()
