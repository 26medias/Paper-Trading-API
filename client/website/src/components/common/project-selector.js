// src/components/common/ProjectSelector.js
import React, { useState } from 'react';
import { Form, Input, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { LockFilled } from '@ant-design/icons';

import './project-selector.less';



const ProjectSelector = ({ data }) => {
    const navigate = useNavigate();
    const [form] = Form.useForm();

    const values = {
        projectName: localStorage.getItem('project')
    }

    const onComplete = (data) => {
        console.log({data})
        localStorage.setItem('project', data.projectName);
        navigate('/market')
    };
    const onFail = console.log;

    return (
        <div className='project-selector'>
            <Form
                form={form}
                name={"project"}
                initialValues={values}
                onFinish={onComplete}
                onFinishFailed={onFail}
                autoComplete="off"
                layout="inline"
            >
                <Form.Item name='projectName' rules={[{ required: true }]}>
                    <Input prefix={<LockFilled className="site-form-item-icon" />} placeholder='Project Name' />
                </Form.Item>
                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        Change
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default ProjectSelector;
